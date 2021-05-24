import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

 
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    password = Column(String(30), nullable=False)
    email = Column(String(30), nullable=False)


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


class UserIDE(Base):
    __tablename__ = 'user_ide'
    id = Column(Integer, primary_key=True)
    version = Column(String(30), nullable=True)
    created = Column(DateTime(30), nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    ide_id = Column(Integer, ForeignKey('ide.id'))
    user = relationship(User)
    ide = relationship(IDE)


class UserRuntimeIntall(Base):
    __tablename__ = 'user_runtime_install'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    runtime_install_id = Column(Integer, ForeignKey('runtime_install.id'))
    user = relationship(User)
    runtime_install = relationship(RuntimeInstall)


def insert_data():
    engine = create_engine('sqlite:///sqlalchemy_example.db')
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
    
    new_user = User(name='john', email='foo@example.com', password='12345678')
    session.add(new_user)
    session.commit()
    
    vscode = IDE(name='vscode')
    intellij = IDE(name='intellij')
    pycharm = IDE(name='pycharm')
    goland = IDE(name='goland')

    session.add(vscode)
    session.add(intellij)
    session.add(pycharm)
    session.add(goland)
    session.commit()    

    user_ide1 = UserIDE(version='1.0.1', user=new_user, ide=vscode)
    user_ide2 = UserIDE(version='1.0.1', user=new_user, ide=intellij)
    user_ide3 = UserIDE(version='1.0.1', user=new_user, ide=pycharm)
    user_ide4 = UserIDE(version='1.0.1', user=new_user, ide=goland)
    session.add(user_ide1)
    session.add(user_ide2)
    session.add(user_ide3)
    session.add(user_ide4)
    session.commit()

    user_repo1 = UserRepo(uri='foo.git', user=new_user)
    user_repo2 = UserRepo(uri='bar.git', user=new_user)
    user_repo3 = UserRepo(uri='baz.git', user=new_user)
    session.add(user_repo1)
    session.add(user_repo2)
    session.add(user_repo3)
    session.commit()


def query_data():
    engine = create_engine('sqlite:///sqlalchemy_example.db')
    Base.metadata.bind = engine    
    DBSession = sessionmaker(bind=engine)
    session = DBSession()    
    userides = session.query(UserIDE).all()
    for useride in userides:
        print(f'{useride.user.name} {useride.ide.name} {useride.version}')

    user_repos = session.query(UserRepo).all()
    for user_repo in user_repos:
        print(f'{user_repo.uri}')


def main(): 
    engine = create_engine('sqlite:///sqlalchemy_example.db')
    Base.metadata.bind = engine
    Base.metadata.drop_all()
    Base.metadata.create_all(engine)
    print("done creating")
    insert_data()
    print("done inserting")
    query_data()


if __name__ == '__main__':
    main()