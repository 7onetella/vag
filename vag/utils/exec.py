import os
import subprocess
import sys
import vag
import inspect
from subprocess import Popen, PIPE
from shlex import split


def get_script_path(relative_path): 
    path = os.path.dirname(inspect.getfile(vag))
    return path + '/scripts/{}'.format(relative_path)


def run(cmd, capture_output=False):
    # https://www.endpoint.com/blog/2015/01/28/getting-realtime-output-using-python
    process = Popen(split(cmd), stdout = PIPE, shell = False, encoding='utf8')

    lines = []
    while True:
        line = process.stdout.readline()
        if line == '' and process.poll() is not None:
            break
        if line and not capture_output:
            print(line.rstrip())
        lines.append(line.rstrip())

    returncode = process.poll()
    return (returncode, lines)