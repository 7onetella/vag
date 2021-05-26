import os
import sys
import shlex
import click
import requests
from os.path import expanduser
from vag.utils import exec
from vag.utils import config
from vag.utils.misc import create_ssh
from vag.utils.cx_db_util import get_build_profile
import yaml

@click.group()
def cx():
    """ CX automation """
    pass


@cx.command()
@click.argument('userid', default='', metavar='<userid>')
@click.argument('password', default='', metavar='<password>')
@click.argument('email', default='', metavar='<email>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def add_user(userid: str, password: str, email: str, debug: bool):
    """builds your project"""
    pass
    

@cx.command()
@click.argument('ide', default='', metavar='<ide>')
@click.argument('userid', default='', metavar='<userid>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def get_profile(ide: str, userid: str, debug: bool):
    """Prints user ide build profile"""

    profile = get_build_profile(ide, userid)
    print(yaml.dump(profile))