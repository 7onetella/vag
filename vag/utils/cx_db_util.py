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


def get_session_future():
    engine = create_engine(get_connection_str())
    Base.metadata.bind = engine        
    return Session(engine, future=True)


db_session = get_session_future()


def find_user_by_username(username: str):
    statement = select(User).filter_by(username=username)
    return db_session.execute(statement).scalars().one()


def find_runtime_install_by_name(runtime_install_name: str):
    statement = select(RuntimeInstall).filter_by(name=runtime_install_name)
    return db_session.execute(statement).scalars().one()


def find_user_runtime_installs_by_user_id(user_id):
    statement = select(UserRuntimeInstall).filter_by(user_id=user_id)
    return db_session.execute(statement).scalars().all()   


def find_user_ides_by_user_id(user_id):
    statement = select(UserIDE).filter_by(user_id=user_id)
    return db_session.execute(statement).scalars().all()   


def find_user_repos_by_user_id(user_id):
    statement = select(UserRepo).filter_by(user_id=user_id)
    return db_session.execute(statement).scalars().all()   


def find_ide_by_name(ide_name: str):
    statement = select(IDE).filter_by(name=ide_name)
    return db_session.execute(statement).scalars().one()


def get_build_profile(ide: str, username: str) -> dict:
    user = find_user_by_username(username)

    statement = select(UserRepo).filter_by(user_id=user.id)
    repositories = db_session.execute(statement).scalars().all()

    statement = select(UserRuntimeInstall).filter_by(user_id=user.id)
    user_runtime_installs = db_session.execute(statement).scalars().all()

    bodies = [ u_r_i.runtime_install.script_body for u_r_i in user_runtime_installs ]
    snppiets = []
    for body in bodies:
        snppiets.append({'body': body})

    return {
        'ide': ide,
        'username': username,
        'password': user.password,
        'email': user.email,
        'private_key': user.private_key,
        'public_key': user.public_key,
        'repositories': [repo.uri for repo in repositories],
        'snippets': snppiets
    }

