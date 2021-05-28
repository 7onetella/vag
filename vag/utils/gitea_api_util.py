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


def create_user(email: str, password: str, username: str):
    api_instance = get_api_instance()
    body = giteapy.CreateUserOption(email = email, password = password, username = username)
    try:
        # Create a user
        api_response = api_instance.admin_create_user(body=body)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AdminApi->admin_create_user: %s\n" % e)


def delete_user(username: str):
    api_instance = get_api_instance()
    try:
        # Create a user
        api_response = api_instance.admin_delete_user(username)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AdminApi->admin_create_user: %s\n" % e)        


def create_user_repo(username: str, repo_name: str):
    api_instance = get_api_instance()
    repository = giteapy.CreateRepoOption(auto_init=True, name=repo_name) # CreateRepoOption |

    try:
        # Create a user
        api_response = api_instance.admin_create_repo(username, repository)
        pprint(api_response)
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