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
import yaml

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
    session = db_session
    new_user = User(username=username, password=password, email=email)
    session.add(new_user)
    session.commit()


@cx.command()
@click.argument('src_username', metavar='<src_username>')
@click.argument('target_username', metavar='<target_username>')
@click.argument('password', metavar='<password>')
@click.argument('email', metavar='<email>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def clone_user(src_username: str, target_username: str, password: str, email: str, debug: bool):
    """Clones user"""

    src_user = find_user_by_username(src_username)

    session = db_session

    new_user = User(username=target_username, password=password, email=email)
    print(f'creating user {new_user.username}')
    session.add(new_user)
    session.commit()

    user_ides = find_user_ides_by_user_id(src_user.id)
    for user_ide in user_ides:
        new_user_ide = UserIDE(user_id=new_user.id, ide_id=user_ide.ide_id)
        print(f'copying user_ide {user_ide.ide.name}')
        session.add(new_user_ide)
        session.commit()       

    ide_runtime_installs = find_ide_runtime_installs_by_user_id(src_user.id)
    for ide_runtime_install in ide_runtime_installs:
        new_ide_runtime_install = IdeRuntimeInstall(user_ide_id=new_user.id, runtime_install_id=ide_runtime_install.runtime_install_id)
        print(f'copying ide_runtime_install {ide_runtime_install.runtime_install.name}')
        session.add(new_ide_runtime_install)
        session.commit()

    user_repos = find_user_repos_by_user_id(src_user.id)        
    for user_repo in user_repos:
        new_user_repo = UserRepo(user_id=new_user.id, uri=user_repo.uri)
        print(f'copying user_repo {user_repo.uri}')
        session.add(new_user_repo)
        session.commit()


@cx.command()
@click.argument('src_username', metavar='<src_username>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def delete_user(src_username: str, debug: bool):
    """Clones user"""

    user = find_user_by_username(src_username)
    session = db_session

    user_runtime_installs = find_user_runtime_installs_by_user_id(user.id)
    for user_runtime_install in user_runtime_installs:
        print(f'deleting user_runtime_install {user_runtime_install.runtime_install.name}')
        session.delete(user_runtime_install)
        session.commit()        

    user_ides = find_user_ides_by_user_id(user.id)
    for user_ide in user_ides:
        print(f'deleting user_ide {user_ide.ide.name}')
        session.delete(user_ide)
        session.commit()            

    user_repos = find_user_repos_by_user_id(user.id)        
    for user_repo in user_repos:
        print(f'deleting user_repo {user_repo.uri}')
        session.delete(user_repo)
        session.commit()

    session = db_session
    print(f'deleting user {user.username}')
    session.delete(user)
    session.commit()


@cx.command()
@click.argument('username', metavar='<username>')
@click.argument('repo', metavar='<repo>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def add_user_repo(username: str, repo: str, debug: bool):
    """add repo to user's list of repos"""

    user = find_user_by_username(username)
    session = db_session
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
    session = db_session
    session.add(runtime_install)
    session.commit()


@cx.command()
@click.argument('username', metavar='<username>')
@click.argument('runtime_install_name', metavar='<runtime_install_name>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def add_user_runtime_install(username: str, runtime_install_name: str, debug: bool):
    """add runtime install to user's list of runtime installs"""

    user = find_user_by_username(username)
    runtime_install = find_runtime_install_by_name(runtime_install_name)
    session = db_session
    user_runtime_install = IdeRuntimeInstall(user_id=user.id, runtime_install_id=runtime_install.id)
    session.add(user_runtime_install)
    session.commit()


@cx.command()
@click.argument('username', metavar='<username>')
@click.argument('ide_name', metavar='<ide_name>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def add_user_ide(username: str, ide_name: str, debug: bool):
    """add runtime install to user's list of runtime installs"""

    user = find_user_by_username(username)
    ide = find_ide_by_name(ide_name)
    session = db_session
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
    session = db_session
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
    session = db_session
    session.add(user)
    session.commit()


yaml.SafeDumper.org_represent_str = yaml.SafeDumper.represent_str

def repr_str(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')
    return dumper.org_represent_str(data)

yaml.add_representer(str, repr_str, Dumper=yaml.SafeDumper)


@cx.command()
@click.argument('username', default='', metavar='<username>')
@click.argument('ide', default='', metavar='<ide>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def get_profile(username: str, ide: str, debug: bool):
    """Prints user ide build profile"""

    profile = get_build_profile(username, ide)
    print(yaml.safe_dump(profile))

