import click
from vag import __version__
from vag.console.commands.vagrant import vagrant
from vag.console.commands.docker import docker
from vag.console.commands.remote import remote
from vag.console.commands.coder import coder

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
root.add_command(coder)


def main():
    root()