import os
import sys
import shlex
import click
import requests
from os.path import expanduser
from vag.utils import exec
from vag.utils import config


@click.group()
def go():
    """ Builder automation """
    pass


@go.command()
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def init(debug: bool):
    """initializes go related config"""

    home = expanduser("~")
    vag_config = f'{home}/.vag.conf'

    if os.path.isfile(vag_config):
        print('config file exists')

    # data = config.read(vag_config)


@go.command()
@click.argument('repo', default='', metavar='<repo>')
@click.argument('branch', default='', metavar='<branch>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def build(repo: str, branch: str, debug: bool):
    """builds your project"""
    script_path = exec.get_script_path(f'go.sh build {repo} {branch}')

    if debug:
        print(f'script_path={script_path}')
    return_code = exec.run_raw(script_path)
    if return_code != 0:
        sys.exit(1)


@go.command()
@click.argument('repo', default='', metavar='<repo>')
@click.argument('stage', default='', metavar='<stage>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def deploy(repo: str, stage: str, debug: bool):
    """builds your project"""
    script_path = exec.get_script_path(f'go.sh deploy {repo} {stage}')
    return_code = exec.run_raw(script_path)
    if return_code != 0:
        sys.exit(1)


@go.command()
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def ssh(debug: bool):
    """SSH into builder"""
    health = requests.get('http://consul.7onetella.net:8500/v1/health/service/builder-dev-builder-service?dc=dc1').json()
    ip = health[0]['Service']['Address']
    port = health[0]['Service']['TaggedAddresses']['lan_ipv4']['Port']

    create_ssh(ip, port)


# CREDIT: https://gist.github.com/bortzmeyer/1284249#gistcomment-3074036
def create_ssh(ip: str, port: str):
    """Create a ssh session"""

    ssh = f'/usr/bin/ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -p {port} builder@{ip}'

    pid = os.fork()
    if pid == 0:  # a child process
        print(f"{ssh}")
        cmd = shlex.split(ssh)
        os.execv(cmd[0], cmd)

    os.wait()
