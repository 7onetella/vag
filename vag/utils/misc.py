import os
import sys
import shlex
import click


# CREDIT: https://gist.github.com/bortzmeyer/1284249#gistcomment-3074036
def create_ssh(ip: str, port: str, user: str, debug: bool, cd_folder: str = None, shell: str = 'bash'):
    """Create a ssh session"""

    ssh = f'/usr/bin/ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -p {port} {user}@{ip}'
    if cd_folder:
        ssh = ssh + f' -t "cd {cd_folder}; {shell} --login"'

    pid = os.fork()
    if pid == 0:  # a child process
        if debug: 
            print(f"{ssh}")
        cmd = shlex.split(ssh)
        os.execv(cmd[0], cmd)

    os.wait()