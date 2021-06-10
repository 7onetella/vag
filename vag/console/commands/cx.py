import os
import sys
import shlex
import click
import requests
from os.path import expanduser

import sqlalchemy
from vag.utils import exec, user_util
from vag.utils import config
from vag.utils.misc import create_ssh
from vag.utils.cx_schema import *
from vag.utils.cx_db_util import *
from vag.utils.cx_test_data import *
import vag.utils.gitea_api_util as gitutil
import yaml
from psycopg2.errors import *
from sqlalchemy.exc import IntegrityError, NoResultFound


@click.group()
def cx():
    """ CX automation """
    pass


@cx.command()
@click.argument('username', metavar='<username>')
@click.argument('password', metavar='<password>')
@click.argument('email', metavar='<email>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def add_user(username: str, password: str, email: str, debug: bool):
    """Adds user"""

    user_util.add_user(username, password, email, '')


@cx.command()
@click.argument('username', metavar='<username>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def delete_user(username: str, debug: bool):
    """Clones user"""

    try:
        user = find_user_by_username(username)
    except NoResultFound:
        print(f'there is no user with name {username}')
        sys.exit(1)

    session = get_session()

    user_ides = find_user_ides_by_user_id(user.id)
    for ui in user_ides:

        ide_runtime_installs = find_ide_runtime_installs_by_user_id(ui.id)
        for i in ide_runtime_installs:
            print(f'deleting ide_runtime_install : {i.runtime_install.name}')
            session.delete(i)

        ide_repos = find_ide_repos_by_user_ide_id(ui.id)        
        for ir in ide_repos:
            print(f'deleting ide_repo            : {ir.uri}')
            session.delete(ir)

        print(f'deleting user_ide            : {ui.ide.name}')
        session.delete(ui)

    user_repos = find_user_repos_by_user_id(user.id)    
    for user_repo in user_repos:
        print(f'deleting user_repo           : {user_repo.uri}')
        session.delete(user_repo)

    session = get_session()
    print(f'deleting user                : {user.username}')
    session.delete(user)
    session.commit()


@cx.command()
@click.argument('username', metavar='<username>')
@click.argument('repo', metavar='<repo>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def add_user_repo(username: str, repo: str, debug: bool):
    """add repo to user's list of repos"""

    user = find_user_by_username(username)
    session = get_session()
    user_repo = UserRepo(uri=repo, user_id=user.id)
    session.add(user_repo)
    session.commit()


@cx.command()
@click.argument('name', metavar='<name>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def add_runtime_install(name: str, debug: bool):
    """add runtime install to user's list of runtime installs"""

    document = ""
    for line in sys.stdin:
        document += line

    runtime_install = RuntimeInstall(name=name, script_body=document)
    session = get_session()
    session.add(runtime_install)
    session.commit()


@cx.command()
@click.argument('username', metavar='<username>')
@click.argument('ide_name', metavar='<ide_name>')
@click.argument('runtime_install_name', metavar='<runtime_install_name>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def add_ide_runtime_install(username: str, ide_name: str, runtime_install_name: str, debug: bool):
    """add runtime install to user's list of runtime installs"""

    user = find_user_by_username(username)
    user_ide = find_user_ide_by_user_id_ide_name(user.id, ide_name)
    runtime_install = find_runtime_install_by_name(runtime_install_name)

    session = get_session()
    user_runtime_install = IDERuntimeInstall(user_ide_id=user_ide.id, runtime_install_id=runtime_install.id)
    session.add(user_runtime_install)
    session.commit()


@cx.command()
@click.argument('username', metavar='<username>')
@click.argument('ide_name', metavar='<ide_name>')
@click.argument('repo', metavar='<repo>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def add_ide_repo(username: str, ide_name: str, repo: str, debug: bool):
    """add repo to user's list of repos"""

    user = find_user_by_username(username)
    session = get_session()
    user_ide = find_user_ide_by_user_id_ide_name(user.id, ide_name)
    ide_repo = IDERepo(uri=repo, user_ide_id=user_ide.id)
    session.add(ide_repo)
    session.commit()


@cx.command()
@click.argument('username', metavar='<username>')
@click.argument('ide_name', metavar='<ide_name>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def add_user_ide(username: str, ide_name: str, debug: bool):
    """add runtime install to user's list of runtime installs"""

    user = find_user_by_username(username)
    ide = find_ide_by_name(ide_name)
    session = get_session()
    user_ide = UserIDE(user_id=user.id, ide_id=ide.id)
    session.add(user_ide)
    session.commit()


@cx.command()
@click.argument('username', metavar='<username>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def user_private_key(username: str, debug: bool):
    """update user private key"""

    document = ""
    for line in sys.stdin:
        document += line

    user = find_user_by_username(username)
    user.private_key = document
    session = get_session()
    session.add(user)
    session.commit()


@cx.command()
@click.argument('username', metavar='<username>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def user_public_key(username: str, debug: bool):
    """update user public key"""

    document = ""
    for line in sys.stdin:
        document += line

    user = find_user_by_username(username)
    user.public_key = document
    session = get_session()
    session.add(user)
    session.commit()


yaml.SafeDumper.org_represent_str = yaml.SafeDumper.represent_str

def repr_str(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')
    return dumper.org_represent_str(data)

yaml.add_representer(str, repr_str, Dumper=yaml.SafeDumper)


@cx.command()
@click.argument('username', metavar='<username>')
@click.argument('ide', metavar='<ide>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def get_profile(username: str, ide: str, debug: bool):
    """Prints user ide build profile"""

    profile = get_build_profile(username, ide)
    print(yaml.safe_dump(profile))


@cx.command()
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def reset_test_data(debug: bool):
    """Resets test data"""

    print('resetting test data')
    reset_test_data_foo()
