from re import I
from vag.utils.crypto_util import genereate_rsa_keys
from vag.utils.cx_schema import *
from vag.utils.cx_db_util import *
from vag.utils import gitea_api_util
from sqlalchemy.exc import IntegrityError, NoResultFound
from random_username.generate import generate_username
from password_generator import PasswordGenerator
import hashlib


def add_user(username: str, password: str, email: str, google_id: str, hashed_email: str, exitOnFailure=True) -> User:
    session = get_session()
    username = username.lower()

    private_key, public_key = genereate_rsa_keys()
    new_user = User(username=username, password=password, email=email, google_id=google_id, private_key=private_key, public_key=public_key, hashed_email=hashed_email)
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
    repo_uri = f'ssh://gitea@git-ssh.curiosityworks.org:2222/{username}/project.git'
    user_repo = UserRepo(uri=repo_uri, user=new_user)
    session.add(user_repo)
    session.commit()

    print("adding user_ide")
    ide = find_ide_by_name('vscode')
    user_ide = UserIDE(user=new_user, ide=ide)
    session.add(user_ide)                          
    session.commit()

    print("adding ide_repo")
    ide_repo = IDERepo(user_ide=user_ide, uri=repo_uri)
    session.add(ide_repo)                          
    session.commit()

    print("adding user_runtime_install")
    runtime_install = find_runtime_install_by_name('tmux')
    user_runtime_install = IDERuntimeInstall(user_ide_id=user_ide.id, runtime_install_id=runtime_install.id)
    session.add(user_runtime_install)
    session.commit()

    gitea_api_util.create_user(username, password, email)
    gitea_api_util.create_user_repo(username, 'project')
    gitea_api_util.create_public_key(username, public_key)

    return new_user


def add_enrollment(email: str, exitOnFailure=True) -> User:
    hashed_email = hashed(email)
    return create_new_user(hashed_email)


def create_new_user(hashed_email: str) -> User:
    random_username = generate_username(1)[0]
    random_username = random_username.lower()
    pwo = PasswordGenerator()
    pwo.minlen = 30 # (Optional)
    pwo.maxlen = 30 # (Optional)
    pwo.minuchars = 2 # (Optional)
    pwo.minlchars = 3 # (Optional)
    pwo.minnumbers = 1 # (Optional)
    pwo.minschars = 0 # (Optional)
    pwo.excludeschars = "!$%^*:="
    random_password = pwo.generate()
    random_email = f'{random_username}@example.com'
    return add_user(f'{random_username}', random_password, random_email, '', hashed_email, exitOnFailure=False)


def hashed(s: str) -> str:
    return hashlib.sha256(bytes(s, 'utf-8')).hexdigest()            


