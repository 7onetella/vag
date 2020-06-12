import click
from vag.utils import exec


@click.group()
def instance():
    """ Vagrant Instance Automation """
    pass


@instance.command()
@click.option('--format', default='text', help='output format')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def list(format, debug):
    """lists running vagrant instances""" 

    script_path = exec.get_script_path('instance/list.sh vagrant tmt')

    exec.run(script_path, format)
    
