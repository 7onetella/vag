import inspect
import os
import sys
import shlex
from shlex import split
from subprocess import Popen, PIPE, STDOUT

import vag


def get_script_path(relative_path): 
    path = os.path.dirname(inspect.getfile(vag))
    return path + '/scripts/{}'.format(relative_path)


def run(cmd, capture_output=False):
    # https://www.endpoint.com/blog/2015/01/28/getting-realtime-output-using-python
    process = Popen(split(cmd), stdout=PIPE, stderr=STDOUT, shell=False, encoding='utf8')

    lines = []
    while True:
        line = process.stdout.readline()

        if line == '' and process.poll() is not None:
            break

        if line and not capture_output:
            print(line.rstrip())
        lines.append(line.rstrip())

    returncode = process.poll()

    return returncode, lines


def run_raw(cmd):
    # os.system preserves ANSI escaped output
    return_code = os.system(cmd)
    return return_code


def fork(cmd_str: str, debug=False):
    if debug:
        print()
        print(cmd_str)
        print

    if sys.stdin.isatty():
        # CREDIT
        # https://gist.github.com/bortzmeyer/1284249#gistcomment-3074036
        pid = os.fork()
        if pid == 0:  # a child process
            cmd = shlex.split(cmd_str)
            os.execv(cmd[0], cmd)

        os.waitpid(pid, 0)

