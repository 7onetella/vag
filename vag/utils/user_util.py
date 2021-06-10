from re import I
from vag.utils.cx_schema import *
from vag.utils.cx_db_util import *
from sqlalchemy.exc import IntegrityError, NoResultFound


def add_user(username: str, password: str, email: str, google_id: str, exitOnFailure=True) -> User:
    session = get_session()
    username = username.lower()
    new_user = User(username=username, password=password, email=email, google_id=google_id)
    session.add(new_user)
    try:
        session.commit()
    except IntegrityError:
        print(f'user {username} already exists')
        if exitOnFailure:
            sys.exit(1)
        else:            
            return None

    print("adding user_repo")
    user_repo = UserRepo(uri=f'ssh://gitea@git-ssh.curiosityworks.org:2222/{username}/project.git ', user=new_user)
    session.add(user_repo)
    session.commit()

    print("adding user_ide")
    ide = find_ide_by_name('vscode')
    user_ide = UserIDE(user=new_user, ide=ide)
    session.add(user_ide)                          
    session.commit()

    print("adding user_runtime_install")
    runtime_install = find_runtime_install_by_name('tmux')
    user_runtime_install = IDERuntimeInstall(user_ide_id=user_ide.id, runtime_install_id=runtime_install.id)
    session.add(user_runtime_install)
    session.commit()

    return new_user