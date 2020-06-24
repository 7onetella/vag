import sys
from os.path import expanduser
import click
from vag.utils import exec
import untangle


@click.group()
def instance():
    """ Vagrant Instance Automation """
    pass


@instance.command()
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def list(debug):
    """lists running vagrant instances""" 

    script_path = exec.get_script_path('instance/list.sh')

    returncode, lines = exec.run(script_path, True)
    if returncode != 0:
        sys.exit(1)
    
    home = expanduser("~")

    for instance in lines:
        if len(instance) > 0:
            f = open(f'{home}/VirtualBox VMs/{instance}/{instance}.vbox', 'r')
            xml_str = f.read()

            obj = untangle.parse(xml_str)
            machine = obj.VirtualBox.Machine
            os_type = machine['OSType']
            memory = machine.Hardware.Memory['RAMSize']
            name = machine['name']
            shared_folder = machine.Hardware.SharedFolders.SharedFolder['hostPath']
            vagrant_f = open(shared_folder+'/Vagrantfile', 'r')
            ip = ''
            for line in vagrant_f.readlines():
                if 'config.vm.network' in line and 'ip:' in line:
                    tokens = line.split(',')
                    for token in tokens:
                        if 'ip:' in token:
                            ip = token.replace('ip:', '').strip().replace('"', '')          

            print(f"""
name   : {name}
shared : {shared_folder}
os     : {os_type}
ip     : {ip}
memory : {memory}""")
            f.close()



