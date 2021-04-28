import os
import click
import sys
from jinja2 import Template
from vag.utils import config
from vag.utils import exec

@click.group()
def docker():
    """ Docker automation """
    pass


@docker.command()
@click.argument('name', default='', metavar='<service>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def deploy(name, debug):
    """deploys docker image in nomad environment"""

    # password-dev:0.8.4
    service = name[:name.rfind('-')]
    group = name[name.rfind('-')+1:name.rfind(':')]
    version = name[name.rfind(':')+1:]

    image = f'docker-registry.7onetella.net/7onetella/{service}:{version}'

    template = Template("""
    job "{{ service }}" {
      datacenters = ["dc1"]

      type = "service"

      update {
        stagger      = "60s"
        max_parallel = 1
      }

      group "{{ group }}" {
        count = 1
        network {
            port "http" { to = {{ port }} }
            port "ssh"  { to = 22 }
        }            
            
        task "{{ service }}-service" {
            driver = "docker"
            config {
                image = "{{ image }}"
                ports = [ "http", "ssh" ]{% if log_driver|length %}
                
                logging {
                   type = "elasticsearch"
                   config {
                        elasticsearch-url="https://elasticsearch-dev.7onetella.net:443"
                        elasticsearch-sniff=false
                        elasticsearch-index="docker-%F"
                        elasticsearch-type="_doc"
                        elasticsearch-timeout="60s"
                        elasticsearch-version=5
                        elasticsearch-fields="containerID,containerName,containerImageName"
                        elasticsearch-bulk-workers=1
                        elasticsearch-bulk-actions=1000
                        elasticsearch-bulk-size=1024
                        elasticsearch-bulk-flush-interval="1s"                   
                    }
                }{% endif %}

                volumes = [
                    "/var/run/docker.sock:/var/run/docker.sock"
                ]                
            }
    
            resources {
                cpu = 20
                memory = {{ memory }}
            }
    
            service {
                tags = ["urlprefix-{{ service }}-{{ group }}.7onetella.net/"]
                port = "http"
                check {
                    type     = "http"
                    path     = "{{ health_check }}"
                    interval = "10s"
                    timeout  = "2s"
                }
            }
    
            env {  {% for key, value in envs.items() %}
                {{ key }} = "{{ value }}"{% endfor %}                
            }
        }
      }
    }""")

    current_dir = os.getcwd()
    app_file = f'{current_dir}/{service}-{group}.app'
    data = config.read(app_file)
    if debug:
        print(f'data is \n {data}')

    # if image is specified use it stead of deriving it from service name
    image_from_config = get(data, 'image', '')
    if image_from_config:
        image = image_from_config

    try:
        os.makedirs(f'/tmp/nomad')
    except OSError:
        # do nothing
        pass

    output = template.render(
        service=service,
        group=group,
        image=image,
        memory=get(data, 'memory', 128),
        port=get(data, 'port', 4242),
        health_check=get(data, 'health', '/api/health'),
        log_driver=get(data, 'log_driver', ''),
        envs=data['envs']
    )
    template_path = f'/tmp/nomad/{service}-{group}.nomad'
    f = open(template_path, 'w+')
    f.write(output)
    f.close()
    if debug:
        print(output)

    script_path = exec.get_script_path(f'nomad.sh {template_path}')
    returncode, lines = exec.run(script_path, False)
    if returncode != 0:
        sys.exit(1)


def get(data: dict, key: str, default_value):
    if key in data:
        return data[key]
    else:
        return default_value








