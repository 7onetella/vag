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


def get_session():
    engine = create_engine(get_connection_str())
    Base.metadata.bind = engine    
    DBSession = sessionmaker(bind=engine)
    return DBSession()


def find_user_by_userid(userid: str):
    engine = create_engine(get_connection_str())
    Base.metadata.bind = engine        
    session = Session(engine, future=True)
    
    statement = select(User).filter_by(userid=userid)
    return session.execute(statement).scalars().one()


def find_runtime_install_by_name(runtime_install_name: str):
    engine = create_engine(get_connection_str())
    Base.metadata.bind = engine        
    session = Session(engine, future=True)
    
    statement = select(RuntimeInstall).filter_by(name=runtime_install_name)
    return session.execute(statement).scalars().one()


def find_ide_by_name(ide_name: str):
    engine = create_engine(get_connection_str())
    Base.metadata.bind = engine        
    session = Session(engine, future=True)
    
    statement = select(IDE).filter_by(name=ide_name)
    return session.execute(statement).scalars().one()


def get_build_profile(ide: str, userid: str) -> dict:
    engine = create_engine(get_connection_str())
    Base.metadata.bind = engine        
    session = Session(engine, future=True)
    
    statement = select(User).filter_by(userid=userid)
    user = session.execute(statement).scalars().all()[0]

    statement = select(UserRepo).filter_by(user_id=user.id)
    repositories = session.execute(statement).scalars().all()

    statement = select(UserRuntimeInstall).filter_by(user_id=user.id)
    user_runtime_installs = session.execute(statement).scalars().all()

    bodies = [ u_r_i.runtime_install.script_body for u_r_i in user_runtime_installs ]
    snppiets = []
    for body in bodies:
        snppiets.append({'body': body})

    return {
        'ide': ide,
        'userid': userid,
        'password': user.password,
        'email': user.email,
        'private_key': user.private_key,
        'public_key': user.public_key,
        'repositories': [repo.uri for repo in repositories],
        'snippets': snppiets
    }

