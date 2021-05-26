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
@click.argument('userid', default='', metavar='<userid>')
@click.argument('password', default='', metavar='<password>')
@click.argument('email', default='', metavar='<email>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def add_user(userid: str, password: str, email: str, debug: bool):
    """builds your project"""
    session = db_session
    new_user = User(userid=userid, password=password, email=email)
    session.add(new_user)
    session.commit()


@cx.command()
@click.argument('userid', default='', metavar='<userid>')
@click.argument('repo', default='', metavar='<repo>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def add_user_repo(userid: str, repo: str, debug: bool):
    """add repo to user's list of repos"""

    user = find_user_by_userid(userid)
    session = db_session
    user_repo = UserRepo(uri=repo, user_id=user.id)
    session.add(user_repo)
    session.commit()


@cx.command()
@click.argument('userid', default='', metavar='<userid>')
@click.argument('runtime_install_name', default='', metavar='<runtime_install_name>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def add_user_runtime_install(userid: str, runtime_install_name: str, debug: bool):
    """add runtime install to user's list of runtime installs"""

    user = find_user_by_userid(userid)
    runtime_install = find_runtime_install_by_name(runtime_install_name)
    session = db_session
    user_runtime_install = UserRuntimeInstall(user_id=user.id, runtime_install_id=runtime_install.id)
    session.add(user_runtime_install)
    session.commit()


@cx.command()
@click.argument('userid', default='', metavar='<userid>')
@click.argument('ide_name', default='', metavar='<ide_name>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def add_user_ide(userid: str, ide_name: str, debug: bool):
    """add runtime install to user's list of runtime installs"""

    user = find_user_by_userid(userid)
    ide = find_ide_by_name(ide_name)
    session = db_session
    user_ide = UserIDE(user_id=user.id, ide_id=ide.id)
    session.add(user_ide)
    session.commit()


@cx.command()
@click.argument('userid', default='', metavar='<userid>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def user_private_key(userid: str, debug: bool):
    """update user private key"""

    document = ""
    for line in sys.stdin:
        document += line

    user = find_user_by_userid(userid)
    user.private_key = document
    session = db_session
    session.add(user)
    session.commit()


@cx.command()
@click.argument('userid', default='', metavar='<userid>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def user_public_key(userid: str, debug: bool):
    """update user public key"""

    document = ""
    for line in sys.stdin:
        document += line

    user = find_user_by_userid(userid)
    user.public_key = document
    session = db_session
    session.add(user)
    session.commit()


@cx.command()
@click.argument('userid', default='', metavar='<userid>')
@click.argument('ide', default='', metavar='<ide>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def get_profile(userid: str, ide: str, debug: bool):
    """Prints user ide build profile"""

    profile = get_build_profile(ide, userid)
    print(yaml.dump(profile))