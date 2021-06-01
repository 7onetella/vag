import os
import sys
import shlex
import click
import requests
from os.path import expanduser
from vag.utils import exec
from vag.utils import config
from vag.utils.misc import create_ssh
from vag.utils.cx_schema import *
from vag.utils.cx_db_util import *
from vag.utils.cx_test_data import *
import vag.utils.gitea_api_util as gitutil
import yaml
from sqlalchemy.exc import NoResultFound

@click.group()
def gitea():
    """ Gitea automation """
    pass


@gitea.command()
@click.argument('username', metavar='<username>')
@click.argument('password', metavar='<password>')
@click.argument('email', metavar='<email>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def add_user(username: str, password: str, email: str, debug: bool):
    """Adds git user"""
    
    gitutil.create_user(username, password, email)


@gitea.command()
@click.argument('username', metavar='<username>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def delete_user(username: str, debug: bool):
    """Deletes git user"""

    gitutil.delete_user(username)


@gitea.command()
@click.argument('username', metavar='<username>')
@click.argument('repo_name', metavar='<repo_name>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def create_user_repo(username: str, repo_name: str, debug: bool):
    """Creates git user repo"""
    gitutil.create_user_repo(username, repo_name)


@gitea.command()
@click.argument('username', metavar='<username>')
@click.argument('repo_name', metavar='<repo_name>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def delete_user_repo(username: str, repo_name: str, debug: bool):
    """Deletes git user repo"""
    try:
        user = find_user_by_username(username)
    except NoResultFound:
        print(f'user {username} does not exist')
        sys.exit(1)
    
    gitutil.delete_user_repo(username, repo_name, user.password, debug)


@gitea.command()
@click.argument('username', metavar='<username>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def list_user_repos(username: str, debug: bool):
    """Deletes git user repo"""
    
    response = gitutil.list_user_repos(username)
    for repo in response:
        print(repo.name)


@gitea.command()
@click.argument('username', metavar='<username>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def create_public_key(username: str, debug: bool):
    """Creates git user public key"""
    
    document = ""
    for line in sys.stdin:
        document += line

    gitutil.create_public_key(username, document)

