import os
import click
import sys
from jinja2 import Template
from vag.utils import config
from vag.utils import exec
from vag.utils.nomadutil import get_version, get_ip_port
from vag.utils.misc import create_ssh, do_scp
from vag.utils.string_util import get_service_and_group


@click.group()
def docker():
    """ Docker automation """
    pass


@docker.command()
@click.argument('semver', default='', metavar='<major|minor|patch>')
@click.argument('name', default='', metavar='<service>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def version(semver: str, name:str, debug: bool):
    """calculate next release version using semver"""

    # password-dev or codeserver-f121-public
    service, group = get_service_and_group(name)
    current_version = get_version(service, group, debug)

    major = int(current_version.split('.')[0])
    minor = int(current_version.split('.')[1])
    patch = int(current_version.split('.')[2])

    if semver == 'major':
        next_major = major + 1
        print(f'{next_major}.{minor}.{patch}')
        return

    if semver == 'minor':
        next_minor = minor + 1
        print(f'{major}.{next_minor}.{patch}')
        return

    if semver == 'patch':
        next_patch = patch + 1
        print(f'{major}.{minor}.{next_patch}')
        return


@docker.command()
@click.argument('repo_name_revision', default='', metavar='<service>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def deploy(repo_name_revision, debug):
    """deploys docker image in nomad environment"""

    # docker-registry.7onetella.net/7onetella/password-dev:0.8.4
    last_slash_idx = repo_name_revision.rfind('/')
    docker_registry_uri = repo_name_revision[:last_slash_idx]
    name_revision = repo_name_revision[last_slash_idx+1:]

    tokens = name_revision.split(':')
    service, group = get_service_and_group(tokens[0])
    if debug:
        print(f'service = {service}, group = {group}')
    version = tokens[1]

    image = f'{docker_registry_uri}/{service}:{version}'
    if debug:
        print(f'image = {image}')

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
            
        task "container" {
            driver = "docker"
            config {
                image = "{{ image }}"
                ports = [ "http", "ssh" ]{% if log_driver is not none %}
                
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
            }{% if health_check is not none %}

            service {
                tags = [ {% for tag in tags %}{% if loop.index0 > 0 %},{% endif %} "{{tag}}"{% endfor %} ]
                port = "http"
                check {
                    type     = "http"
                    path     = "{{ health_check }}"
                    interval = "10s"
                    timeout  = "2s"
                }
            }{% else %}

            service {
                port = "ssh"
            }{% endif %}
    
            env {  {% for key, value in envs.items() %}
                {{ key }} = "{{ value }}"{% endfor %}                
            }
        }
      }
    }""")

    current_dir = os.getcwd()
    app_file = f'{current_dir}/{service}-{group}.app'
    if debug:
        print(f'app_file = {app_file}')
        
    try:
        data = config.read(app_file)
    except IndexError:
        print(f'error while processing {app_file}')
        sys.exit(1)

    if debug:
        print(f'data is \n {data}')

    # if image is specified use it stead of deriving it from service name
    image_from_config = get(data, 'image', '')
    if image_from_config:
        image = image_from_config

    tags = data['tags']

    if not tags:        
        urlprefix = f'urlprefix-{ service }-{ group }.7onetella.net/'

        host = get(data, 'host', '')
        path = get(data, 'path', '/')
        if host:
            urlprefix = f'urlprefix-{host}{path}'

        tags.append(urlprefix)
    if debug:
        print(f'tags = {tags}')

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
        health_check=get(data, 'health', None),
        log_driver=get(data, 'log_driver', None),
        tags=tags,
        envs=data['envs']
    )
    template_path = f'/tmp/nomad/{service}-{group}.nomad'
    f = open(template_path, 'w+')
    f.write(output)
    f.close()
    if debug:
        print(output)
        return 0

    script_path = exec.get_script_path(f'nomad.sh {template_path}')
    returncode, lines = exec.run(script_path, False)
    if returncode != 0:
        sys.exit(1)


@docker.command()
@click.argument('name', default='', metavar='<service>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def ssh(name:str, debug: bool):
    """SSH into docker container"""
    service, group = get_service_and_group(name)

    ip, port = get_ip_port(service, group, debug)
    if debug:
        print(f'ip = {ip}, port = {port}')
    
    landing_path = '/home/coder'
    if 'codeserver' in service:
        landing_path = '/home/coder/workspace'

    create_ssh(ip, port, 'coder', debug, landing_path, 'zsh')


@docker.command()
@click.argument('name', default='', metavar='<service>')
@click.argument('src', default='', metavar='<src>')
@click.argument('target', default='', metavar='<target>')
@click.option('--show', is_flag=True, default=False, help='print scp command')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def scp(name:str, src: str, target: str, show: bool, debug: bool):
    """SCP to docker container"""
    service, group = get_service_and_group(name)

    ip, port = get_ip_port(service, group, debug)
    if debug:
        print(f'ip = {ip}, port = {port}')

    do_scp(ip, port, 'coder', src, target, show, debug)


def get(data: dict, key: str, default_value):
    if key in data:
        return data[key]
    else:
        if default_value:
            return default_value
        else:
            return None








