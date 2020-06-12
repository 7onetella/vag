import click
from os.path import expanduser
from vag import __version__
from vag.console.commands.instance import instance


@click.group()
def root():
    pass


@root.command()
def version():
    """Prints version"""
    
    print(__version__)


@root.command()
@click.argument('box', default='7onetella/ubuntu-19.10', metavar='<box>')
@click.argument('hostname', default='', metavar='<hostname>')
@click.argument('ip_address', default='', metavar='<ip_address>')
@click.option('--interface', default='eno1', help='network interface')
@click.option('--memory', default='1024', help='memory')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def init(box, hostname, ip_address, interface, memory, debug):
    """Initializes a new Vagrantfile"""

    home = expanduser("~")

    template = f"""
Vagrant.configure("2") do |config|

  config.vm.box = "{box}"
  config.vm.box_url = "file://{home}/.vagrant_boxes/{box}/package.box"

  config.vm.network "public_network", ip: "{ip_address}", bridge: "{interface}"

  config.vm.provider "virtualbox" do |vb|
    vb.memory = "{memory}"
  end

  config.vm.hostname = "{hostname}"
  config.ssh.insert_key = false # 1
  config.ssh.private_key_path = ['~/.vagrant.d/insecure_private_key', '~/.ssh/id_rsa'] # 2
  config.vm.provision "file", source: "~/.ssh/id_rsa.pub", destination: "~/.ssh/authorized_keys" # 3

end"""

    f = open('./Vagrantfile','w+')
    f.write(template)
    f.close()
    print(template)


root.add_command(version)
root.add_command(instance)
root.add_command(init)


def main():
    root()