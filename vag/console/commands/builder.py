import os
import sys
import shlex
import click
from vag.utils import exec


@click.group()
def go():
    """ Builder automation """
    pass


@go.command()
@click.argument('repo', default='', metavar='<repo>')
@click.argument('branch', default='', metavar='<branch>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def build(repo: str, branch: str, debug: bool):
    """builds your project"""
    script_path = exec.get_script_path(f'go.sh build {repo} {branch}')
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
    """ssh into builder"""
    pass


# CREDIT: https://gist.github.com/bortzmeyer/1284249#gistcomment-3074036
def create_ssh(port: str, ip: str):
    """Create a ssh session"""

    ssh = f'/usr/bin/ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -p {port} root@{ip}'
    print()
    print(ssh)
    print()

    pid = os.fork()
    if pid == 0:  # a child process
        print(f"{ssh}")
        cmd = shlex.split(ssh)
        os.execv(cmd[0], cmd)

    os.wait(pid, 0)
