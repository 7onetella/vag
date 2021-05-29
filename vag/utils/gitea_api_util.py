from __future__ import print_function
import time
import giteapy
from giteapy.rest import ApiException
from pprint import pprint
import os


def get_api_instance() -> giteapy.AdminApi:
    configuration = giteapy.Configuration()
    configuration.api_key['access_token'] = os.getenv('GITEA_ACCESS_TOKEN')
    configuration.host = 'https://git.curiosityworks.org/api/v1'
    return giteapy.AdminApi(giteapy.ApiClient(configuration))


def get_user_api_instance() -> giteapy.UserApi:
    configuration = giteapy.Configuration()
    configuration.api_key['access_token'] = os.getenv('GITEA_ACCESS_TOKEN')
    configuration.host = 'https://git.curiosityworks.org/api/v1'
    return giteapy.UserApi(giteapy.ApiClient(configuration))


def get_repository_api_instance() -> giteapy.RepositoryApi():
    configuration = giteapy.Configuration()
    configuration.api_key['access_token'] = os.getenv('GITEA_ACCESS_TOKEN')
    configuration.host = 'https://git.curiosityworks.org/api/v1'
    return giteapy.RepositoryApi(giteapy.ApiClient(configuration))


def create_user(username: str, password: str, email: str):
    api_instance = get_api_instance()
    body = giteapy.CreateUserOption(email = email, password = password, username = username, must_change_password=False)
    try:
        # Create a user
        api_response = api_instance.admin_create_user(body=body)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AdminApi->admin_create_user: %s\n" % e)


def delete_user(username: str, debug: bool=False):
    api_instance = get_api_instance()
    try:
        # Create a user
        api_response = api_instance.admin_delete_user(username)
        pprint(api_response)
    except ApiException as e:
        if debug:
            print("Exception when calling AdminApi->admin_create_user: %s\n" % e)        
        print("deleting user failed")
    except Exception as e:
        print("deleting user failed")


def create_user_repo(username: str, repo_name: str, debug: bool=False):
    api_instance = get_api_instance()
    repository = giteapy.CreateRepoOption(auto_init=True, name=repo_name) # CreateRepoOption |

    try:
        # Create a user
        return api_instance.admin_create_repo(username, repository)
    except ApiException as e:
        if debug:
            print("Exception when calling create_user_repo: %s\n" % e)                
        print(f'failed to create user repo {repo_name}')


def delete_user_repo(username: str, repo_name: str, debug: bool=False):
    api_instance = get_repository_api_instance()

    try:
        # Create a user
        api_response = api_instance.repo_delete(username, repo_name)
        pprint(api_response)
    except ApiException as e:
        if debug:
            print("Exception when calling create_user_repo: %s\n" % e)                
        print(f'failed to delete user repo {repo_name}')


def list_user_repos(username: str):
    api_instance = get_user_api_instance()

    try:
        # Create a user
        api_response = api_instance.user_current_list_repos(async_req=False)
        # pprint(api_response)
        return api_response
    except ApiException as e:
        print("Exception when calling AdminApi->admin_create_user: %s\n" % e)                


def create_public_key(username: str, key_body: str):
    api_instance = get_api_instance()
    key = giteapy.CreateKeyOption(key=key_body, read_only=False, title=f'{username} public key') # CreateKeyOption |  (optional)

    try:
        # Create a user
        api_response = api_instance.admin_create_public_key(username, key=key)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AdminApi->admin_create_user: %s\n" % e)                        