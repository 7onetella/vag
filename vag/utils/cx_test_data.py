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

    new_user = User(username='john', email='foo@example.com', password='12345678', private_key="""rsa key start here 


ras key end here""", public_key='rsa public key')
    session.add(new_user)
    session.commit()

    user_ide_vscode = UserIDE(user=new_user, ide=vscode)
    user_ide_intellij = UserIDE(user=new_user, ide=intellij)
    user_ide_pycharm = UserIDE(user=new_user, ide=pycharm)
    user_ide_goland = UserIDE(user=new_user, ide=goland)
    session.add(user_ide_vscode)
    session.add(user_ide_intellij)
    session.add(user_ide_pycharm)
    session.add(user_ide_goland)
    session.commit()

    session.add(UserRepo(uri='foo.git', user=new_user))
    session.add(UserRepo(uri='bar.git', user=new_user))
    session.add(UserRepo(uri='baz.git', user=new_user))
    session.commit()

    session.add(IdeRuntimeInstall(user_ide=user_ide_vscode, runtime_install=ember_install))
    session.add(IdeRuntimeInstall(user_ide=user_ide_intellij, runtime_install=tmux_install))
    session.add(IdeRuntimeInstall(user_ide=user_ide_pycharm, runtime_install=gh_cli_install))
    session.add(IdeRuntimeInstall(user_ide=user_ide_goland, runtime_install=gh_cli_install))
    session.commit()


def main(): 
    engine = create_engine(get_connection_str())
    insert_data()
    

if __name__ == '__main__':
    main()