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

def user_foo_test_data():
    engine = create_engine(get_connection_str())
    Base.metadata.bind = engine    
    DBSession = sessionmaker(bind=engine)
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


    ember_install = RuntimeInstall(name='emberjs', script_body="""# ember
sudo sudo npm install -g ember-cli
""")
    tmux_install = RuntimeInstall(name='tmux', script_body="""# tmux
sudo apt-get install -y tmux
echo -e "\n\nalias s='tmux new -A -s shared'" >> /home/coder/.zshrc
""")
    gh_cli_install = RuntimeInstall(name='github cli', script_body="""# github cli gh install
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt-get update
sudo apt-get install gh
""")
    poetry_install = RuntimeInstall(name='poetry', script_body="""# poetry
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
echo -e "export PATH=\"\$HOME/.poetry/bin:\$PATH\"" >> ~/.zshrc
""")
    postgresql_install = RuntimeInstall(name='postgres', script_body="""# vag dependencies
sudo apt-get install -y postgresql
sudo apt-get install -y libpq-dev
""")
    session.add(ember_install)
    session.add(tmux_install)
    session.add(gh_cli_install)
    session.add(poetry_install)
    session.add(postgresql_install)
    session.commit()

    # ----------- user related instance tables -----------

    new_user = User(username='foo', email='foo@gmail.com', password='teachmecoding', private_key="""-----BEGIN RSA PRIVATE KEY-----
-----END RSA PRIVATE KEY-----""", public_key='rsa public key', google_id='1234')
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

    session.add(IDERuntimeInstall(user_ide=user_ide_vscode, runtime_install=ember_install))
    session.add(IDERuntimeInstall(user_ide=user_ide_vscode, runtime_install=tmux_install))
    session.add(IDERuntimeInstall(user_ide=user_ide_vscode, runtime_install=gh_cli_install))
    session.add(IDERuntimeInstall(user_ide=user_ide_vscode, runtime_install=poetry_install))
    session.add(IDERuntimeInstall(user_ide=user_ide_vscode, runtime_install=postgresql_install))
    session.commit()

    containers_repo = UserRepo(uri='git@github.com:foo/containers.git', user=new_user)
    vag_repo = UserRepo(uri='git@github.com:foo/vag.git', user=new_user)
    sites_repo = UserRepo(uri='git@github.com:foo/sites.git', user=new_user)
    users_repo = UserRepo(uri='git@github.com:foo/users.git', user=new_user)
    session.add(containers_repo)
    session.add(vag_repo)
    session.add(sites_repo)
    session.add(users_repo)
    session.commit()

    session.add(IDERepo(user_ide=user_ide_vscode, uri=containers_repo.uri))    
    session.add(IDERepo(user_ide=user_ide_vscode, uri=vag_repo.uri))    
    session.add(IDERepo(user_ide=user_ide_vscode, uri=sites_repo.uri))    
    session.add(IDERepo(user_ide=user_ide_vscode, uri=users_repo.uri))    
    session.commit()


def reset_test_data_foo(): 
    engine = create_engine(get_connection_str())
    Base.metadata.bind = engine
    Base.metadata.drop_all()
    Base.metadata.create_all(engine)
    user_foo_test_data()
    

if __name__ == '__main__':
    reset_test_data_foo()