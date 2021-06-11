import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
import yaml
from sqlalchemy import select
from flask_login import UserMixin


def get_connection_str():
    return os.getenv('CX_DB_CONN')


Base = declarative_base()


class UserObj(UserMixin):
    def __init__(self, id_, name, email):
        self.id = id_
        self.name = name
        self.email = email


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    google_id = Column(String(64), nullable=True, unique=False) 
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    email = Column(String(50), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True) 
    private_key = Column(String(4000), nullable=True)
    public_key = Column(String(1000), nullable=True)


class IDE(Base):
    __tablename__ = 'ide'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
 

class UserRepo(Base):
    __tablename__ = 'user_repo'
    id = Column(Integer, primary_key=True)
    uri = Column(String(100))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


class RuntimeInstall(Base):
    __tablename__ = 'runtime_install'
    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True)
    script_body = Column(String(4000))


class UserIDE(Base):
    __tablename__ = 'user_ide'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    ide_id = Column(Integer, ForeignKey('ide.id'))
    user = relationship(User)
    ide = relationship(IDE)


class IDERuntimeInstall(Base):
    __tablename__ = 'ide_runtime_install'
    id = Column(Integer, primary_key=True)
    user_ide_id = Column(Integer, ForeignKey('user_ide.id'))
    runtime_install_id = Column(Integer, ForeignKey('runtime_install.id'))
    user_ide = relationship(UserIDE)
    runtime_install = relationship(RuntimeInstall)


class IDERepo(Base):
    __tablename__ = 'ide_repo'
    id = Column(Integer, primary_key=True)
    user_ide_id = Column(Integer, ForeignKey('user_ide.id'))
    user_ide = relationship(UserIDE)
    uri = Column(String(100))


def query_data():
    engine = create_engine(get_connection_str())
    Base.metadata.bind = engine    
    DBSession = sessionmaker(bind=engine)
    session = DBSession()    
    usernames = session.query(UserIDE).all()
    for username in usernames:
        print(f'{username.ide.name}-{username.user.username}')

    user_repos = session.query(UserRepo).all()
    for user_repo in user_repos:
        print(f'{user_repo.uri}')

    user_runtime_installs = session.query(IDERuntimeInstall).all()
    for user_runtime_install in user_runtime_installs:
        print(f'{user_runtime_install.runtime_install.name}')


def drop_create_schema(): 
    engine = create_engine(get_connection_str())
    Base.metadata.bind = engine
    Base.metadata.drop_all()
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    drop_create_schema()