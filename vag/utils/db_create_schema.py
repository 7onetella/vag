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


def insert_data():
    engine = create_engine(get_connection_str())
    # Bind the engine to the metadata of the Base class so that the
    # declaratives can be accessed through a DBSession instance
    Base.metadata.bind = engine
    
    DBSession = sessionmaker(bind=engine)
    # A DBSession() instance establishes all conversations with the database
    # and represents a "staging zone" for all the objects loaded into the
    # database session object. Any change made against the objects in the
    # session won't be persisted into the database until you call
    # session.commit(). If you're not happy about the changes, you can
    # revert all of them back to the last commit by calling
    # session.rollback()
    session = DBSession()
    
    # ----------- meta data tables -----------
    vscode = IDE(name='vscode')
    intellij = IDE(name='intellij')
    pycharm = IDE(name='pycharm')
    goland = IDE(name='goland')
    session.add(vscode)
    session.add(intellij)
    session.add(pycharm)
    session.add(goland)
    session.commit()    

    ember_install = RuntimeInstall(name='emberjs', script_body='emberjs install script')
    tmux_install = RuntimeInstall(name='tmux', script_body='tmux install script')
    gh_cli_install = RuntimeInstall(name='github cli', script_body='gh install script')
    session.add(ember_install)
    session.add(tmux_install)
    session.add(gh_cli_install)
    session.commit()

    # ----------- user related instance tables -----------

    new_user = User(userid='john', email='foo@example.com', password='12345678', private_key="""rsa key start here 


ras key end here""", public_key='rsa public key')
    session.add(new_user)
    session.commit()

    session.add(UserIDE(user=new_user, ide=vscode))
    session.add(UserIDE(user=new_user, ide=intellij))
    session.add(UserIDE(user=new_user, ide=pycharm))
    session.add(UserIDE(user=new_user, ide=goland))
    session.commit()

    session.add(UserRepo(uri='foo.git', user=new_user))
    session.add(UserRepo(uri='bar.git', user=new_user))
    session.add(UserRepo(uri='baz.git', user=new_user))
    session.commit()

    session.add(UserRuntimeInstall(user=new_user, runtime_install=ember_install))
    session.add(UserRuntimeInstall(user=new_user, runtime_install=tmux_install))
    session.add(UserRuntimeInstall(user=new_user, runtime_install=gh_cli_install))
    session.commit()


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


def get_profile(ide: str, userid: str) -> dict:
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
        'password': user.password,
        'email': user.email,
        'private_key': user.private_key,
        'public_key': user.public_key,
        'repositories': [repo.uri for repo in repositories],
        'snippets': snppiets
    }

def main(): 
    engine = create_engine(get_connection_str())

    Base.metadata.bind = engine
    Base.metadata.drop_all()
    Base.metadata.create_all(engine)
    insert_data()

    # query_data()

    print()
    profile = get_profile("vscode", "john")
    print(yaml.dump(profile))



if __name__ == '__main__':
    main()