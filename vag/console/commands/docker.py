import os
import click
import sys
from jinja2 import Template
from vag.utils import config
from vag.utils import exec
from vag.utils.nomadutil import get_version, get_ip_port
from vag.utils.misc import create_ssh, do_scp
from vag.utils.string_util import get_service_and_group
import yaml
import stat


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


@docker.command()
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def pre_build(debug: bool):
    """Generates config files need by docker build"""

    document = ""
    # if tty
    # if sys.stdin.isatty():
    #     document = read_file(f'./profile-{username}.yml')
    # else: # if pipe
    for line in sys.stdin:
        document += line

    profile = yaml.load(document, Loader=yaml.FullLoader)
    if debug: 
        print(f'profile = {profile}')

    username = profile['username']
    password = profile['password']
    email = profile['email']

    # ------------------------------------------------------------------
    if 'private_key' in profile:
        try:
            os.makedirs(f'./.ssh', mode=0o700)
        except OSError:
            # do nothing
            pass
        if profile['private_key']:
            write_file('./.ssh/id_rsa', profile['private_key'])
            st = os.stat('./.ssh/id_rsa')
            os.chmod('./.ssh/id_rsa', stat.S_IRUSR | stat.S_IWUSR)

    # ------------------------------------------------------------------
    write_file('./config.yml', render_template("""bind-addr: 0.0.0.0:9991
auth: password
password: {{ password }}
cert: false    
""", password=password))

    # ------------------------------------------------------------------
    write_file('./.gitconfig', render_template("""[credential]
        helper = store
[user]
	name = {{ username }}
	email = {{ email }}""", username=username, email=email))

    # ------------------------------------------------------------------
    app_file_path = f'./{profile["ide"]}-{username}-public.app'
    write_file(app_file_path, render_template("""[vscode]
memory  = 2048
port    = 9991
health  = /
host    = {{ ide }}-{{ username }}.curiosityworks.org
""", username=username, ide=profile['ide']))

    # ------------------------------------------------------------------
    if 'repositories' in profile and profile['repositories']:
        write_file('./repositories.txt', render_template("""{% for repo_uri in repositories %}{% if loop.index0 > 0 %}\n{% endif %}{{ repo_uri }}{% endfor %}""", repositories=profile['repositories']))
    else:
        write_file('./repositories.txt', '')
        
    # ------------------------------------------------------------------
    if 'snippets' in profile:
        snippets = [snippet['body'] for snippet in profile['snippets']]    
        write_file('./runtime_install.sh', render_template("""#!/bin/bash -e
    
set -x

{% for snippet in snippets %}{{ snippet }}

{% endfor %}# snippets end here""", snippets=snippets))
        st = os.stat('./runtime_install.sh')
        os.chmod('./runtime_install.sh', st.st_mode | stat.S_IEXEC)
    # ------------------------------------------------------------------
    if True:
        write_file('./gotty.sh', render_template("""#!/bin/sh

export TERM=xterm

/home/coder/go/bin/gotty --ws-origin "vscode-{{ username }}.curiosityworks.org" -p 2222 -c {{ username }}:{{ password }} -w /usr/bin/zsh >>/dev/null 2>&1 
""", username=username, password=password))
        st = os.stat('./gotty.sh')
        os.chmod('./gotty.sh', st.st_mode | stat.S_IEXEC)


@docker.command()
@click.argument('service', default='', metavar='<service>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def post_build(service: str, debug: bool):
    """Deletes config files generated in pre-build"""

    delete_file('./.ssh/id_rsa')

    delete_file('./config.yml')

    delete_file('./.gitconfig')

    delete_file(f'{service}-public.app')

    delete_file('./repositories.txt')

    delete_file('./runtime_install.sh')

    delete_file('./gotty.sh')


def get(data: dict, key: str, default_value):
    if key in data:
        return data[key]
    else:
        if default_value:
            return default_value
        else:
            return None


def write_file(file_path: str, body: str):
    print(f'writing {file_path}')
    f = open(file_path, 'w+')
    f.write(body)
    f.close()


def read_file(file_path: str) -> str:
    print(f'reading {file_path}')
    f = open(file_path, 'r')
    body = f.read()
    f.close()
    return body


def delete_file(file_path: str):
    if os.path.exists(file_path):
        print(f'deleting {file_path}')
        os.remove(file_path)


def render_template(tpl_body: str, **kwargs):
    template = Template(tpl_body)
    output = template.render(
        kwargs
    )
    return output




