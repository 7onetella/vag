from __future__ import print_function
import time
import giteapy
from giteapy.rest import ApiException
from pprint import pprint
import os

def get_api_instance():
    configuration = giteapy.Configuration()
    configuration.api_key['access_token'] = os.getenv('GITEA_ACCESS_TOKEN')
    configuration.host = 'https://git.curiosityworks.org/api/v1'
    api_instance = giteapy.AdminApi(giteapy.ApiClient(configuration))


def create_user(email: str, password: str, username: str):
    api_instance = get_api_instance()
    body = giteapy.CreateUserOption(email = email, password = password, username = username)
    try:
        # Create a user
        api_response = api_instance.admin_create_user(body=body)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AdminApi->admin_create_user: %s\n" % e)