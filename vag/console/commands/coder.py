import os
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
    allocations = requests.get('http://nomad.7onetella.net:4646/v1/job/codeserver/allocations').json()
    alloc_id = allocations[0]['ID']

    alloc = requests.get(f'http://nomad.7onetella.net:4646/v1/allocation/{alloc_id}').json()

    ip = alloc['Resources']['Networks'][0]['IP']
    dynamic_ports = alloc['Resources']['Networks'][0]['DynamicPorts']
    port = ''
    for p in dynamic_ports:
        if p['Label'] == 'ssh':
            port = p['Value']
            break

    create_ssh(ip, port, 'coder', debug)