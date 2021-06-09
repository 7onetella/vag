from vag.utils.cx_schema import *
from vag.utils.cx_db_util import *
from sqlalchemy.exc import IntegrityError, NoResultFound


def add_user(username: str, password: str, email: str, exitOnFailure=True) -> User:
    session = get_session()
    new_user = User(username=username, password=password, email=email)
    session.add(new_user)
    try:
        session.commit()
    except IntegrityError:
        print(f'user {username} already exists')
        if exitOnFailure:
            sys.exit(1)
        else:            
            return None

    return new_user