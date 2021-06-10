import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
import yaml
from sqlalchemy import select
from vag.utils.cx_schema import *
import time


def init_session_future():
    conn_str = get_connection_str()
    if not conn_str:
        return None
    engine = create_engine(conn_str)
    return Session(engine)


db_session = init_session_future()


def get_session(): 
    conn_str = get_connection_str()
    if not conn_str:
        print('CX_DB_CONN must be set')
        sys.exit(1)

    return db_session


def find_one(statement):
    try:
        return get_session().execute(statement).scalars().one()    
    except:
        return None


def find_user_by_google_id(google_id: str) -> User:
    statement = select(User).filter_by(google_id=google_id)
    return find_one(statement) 


def find_user_by_username(username: str) -> User:
    statement = select(User).filter_by(username=username)
    return get_session().execute(statement).scalars().one()


def find_runtime_install_by_name(runtime_install_name: str):
    statement = select(RuntimeInstall).filter_by(name=runtime_install_name)
    return get_session().execute(statement).scalars().one()


def find_ide_runtime_installs_by_user_id(user_ide_id):
    statement = select(IDERuntimeInstall).filter_by(user_ide_id=user_ide_id)
    return get_session().execute(statement).scalars().all()   


def find_user_ides_by_user_id(user_id):
    statement = select(UserIDE).filter_by(user_id=user_id)
    return get_session().execute(statement).scalars().all()   


def find_user_ide_by_user_id_ide_name(user_id, ide_name: str):
    user_ides = find_user_ides_by_user_id(user_id)
    for user_ide in user_ides:
        if user_ide.ide.name == ide_name:
            return user_ide

def find_user_repos_by_user_id(user_id):
    statement = select(UserRepo).filter_by(user_id=user_id)
    return get_session().execute(statement).scalars().all()   


def find_ide_repos_by_user_ide_id(user_ide_id):
    statement = select(IDERepo).filter_by(user_ide_id=user_ide_id)
    return get_session().execute(statement).scalars().all()   


def find_ide_by_name(ide_name: str):
    statement = select(IDE).filter_by(name=ide_name)
    return get_session().execute(statement).scalars().one()


def get_build_profile(username: str, ide_name: str) -> dict:
    user = find_user_by_username(username)

    user_ide = find_user_ide_by_user_id_ide_name(user.id, ide_name)

    ide_repos = find_ide_repos_by_user_ide_id(user_ide.id)

    statement = select(IDERuntimeInstall).filter_by(user_ide=user_ide)
    user_ide_runtime_installs = get_session().execute(statement).scalars().all()

    bodies = [ u_r_i.runtime_install.script_body for u_r_i in user_ide_runtime_installs ]
    snppiets = []
    for body in bodies:
        snppiets.append({'body': body})

    return {
        'ide': ide_name,
        'username': username,
        'password': user.password,
        'email': user.email,
        'private_key': user.private_key,
        'public_key': user.public_key,
        'repositories': [repo.uri for repo in ide_repos],
        'snippets': snppiets
    }

