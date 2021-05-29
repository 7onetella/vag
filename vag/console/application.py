import click
from vag import __version__
from vag.console.commands.vagrant import vagrant
from vag.console.commands.docker import docker
from vag.console.commands.remote import remote
from vag.console.commands.cx import cx
from vag.console.commands.gitea import gitea


@click.group()
def root():
    pass


@root.command()
def version():
    """Prints version"""
    print(__version__)


root.add_command(version)
root.add_command(vagrant)
root.add_command(docker)
root.add_command(remote)
root.add_command(cx)
root.add_command(gitea)


def main():
    root()