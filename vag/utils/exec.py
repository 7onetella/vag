import inspect
import os
from shlex import split
from subprocess import Popen, PIPE

import vag


def get_script_path(relative_path): 
    path = os.path.dirname(inspect.getfile(vag))
    return path + '/scripts/{}'.format(relative_path)


def run(cmd, capture_output=False):
    # https://www.endpoint.com/blog/2015/01/28/getting-realtime-output-using-python
    process = Popen(split(cmd), stdout=PIPE, stderr=PIPE, shell=False, encoding='utf8')

    lines = []
    err_line = ''
    while True:
        line = process.stdout.readline()
        if line == '':
            err_line = process.stderr.readline()

        if line == '' and err_line == '' and process.poll() is not None:
            break

        if line and not capture_output:
            print(line.rstrip())
        lines.append(line.rstrip())

        if err_line and not capture_output:
            print(err_line.rstrip())
        lines.append(err_line.rstrip())

    returncode = process.poll()

    return returncode, lines
