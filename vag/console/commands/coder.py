import os
from vag.utils.nomadutil import get_ip_port
import click
import sys
import requests
from vag.utils.misc import create_ssh

@click.group()
def coder():
    """ Coder automation """
    pass


@coder.command()
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def ssh(debug: bool):
    """SSH into codeserver"""
    ip, port = get_ip_port('codeserver', debug)
    if debug:
        print(f'ip = {ip}, port = {port}')

    create_ssh(ip, port, 'coder', debug, '/home/coder/workspace', 'zsh')