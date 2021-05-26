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


def get_connection_str():
    return 'postgresql://cxuser:cxdev114@tmt-vm11.7onetella.net:5432/devdb'


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    userid = Column(String(30), nullable=False)
    password = Column(String(30), nullable=False)
    email = Column(String(30), nullable=False)
    private_key = Column(String(2000), nullable=True)
    public_key = Column(String(500), nullable=True)


class IDE(Base):
    __tablename__ = 'ide'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
 

class UserRepo(Base):
    __tablename__ = 'user_repo'
    id = Column(Integer, primary_key=True)
    uri = Column(String(50))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


class RuntimeInstall(Base):
    __tablename__ = 'runtime_install'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    script_body = Column(String(4000))


class UserRuntimeInstall(Base):
    __tablename__ = 'user_runtime_install'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    runtime_install_id = Column(Integer, ForeignKey('runtime_install.id'))
    user = relationship(User)
    runtime_install = relationship(RuntimeInstall)


class UserIDE(Base):
    __tablename__ = 'user_ide'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    ide_id = Column(Integer, ForeignKey('ide.id'))
    user = relationship(User)
    ide = relationship(IDE)


def query_data():
    engine = create_engine(get_connection_str())
    Base.metadata.bind = engine    
    DBSession = sessionmaker(bind=engine)
    session = DBSession()    
    userides = session.query(UserIDE).all()
    for useride in userides:
        print(f'{useride.ide.name}-{useride.user.userid}')

    user_repos = session.query(UserRepo).all()
    for user_repo in user_repos:
        print(f'{user_repo.uri}')

    user_runtime_installs = session.query(UserRuntimeInstall).all()
    for user_runtime_install in user_runtime_installs:
        print(f'{user_runtime_install.runtime_install.name}')


def main(): 
    engine = create_engine(get_connection_str())
    Base.metadata.bind = engine
    Base.metadata.drop_all()
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    main()