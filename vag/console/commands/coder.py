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
    if debug:
        print(allocations)

    alloc_id = ''
    for a in allocations:
        if a['TaskStates']['codeserver-service']['State'] == 'running':
            alloc_id = a['ID']

    if debug:
        print(f'alloc_id = {alloc_id}')

    alloc = requests.get(f'http://nomad.7onetella.net:4646/v1/allocation/{alloc_id}').json()
    if debug:
        print(alloc)

    ip = alloc['Resources']['Networks'][0]['IP']
    dynamic_ports = alloc['Resources']['Networks'][0]['DynamicPorts']
    port = ''
    for p in dynamic_ports:
        if p['Label'] == 'ssh':
            port = p['Value']
            break

    create_ssh(ip, port, 'coder', debug, '/home/coder/workspace', 'zsh')