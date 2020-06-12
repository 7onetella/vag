import click
from vag import __version__
from vag.console.commands.instance import instance


@click.group()
def main():
    pass


@main.command()
def version():
    """Prints version"""
    
    print(__version__)


main.add_command(version)
main.add_command(instance)


if __name__ == '__main__':
    main()