import click
from os.path import expanduser
from vag import __version__
from vag.console.commands.instance import instance
from jinja2 import Template


@click.group()
def root():
    pass


@root.command()
def version():
    """Prints version"""
    
    print(__version__)


@root.command()
@click.argument('box', default='7onetella/ubuntu-20.04', metavar='<box>')
@click.argument('hostname', default='', metavar='<hostname>')
@click.argument('ip_address', default='', metavar='<ip_address>')
@click.option('--interface', default='eno1', help='network interface')
@click.option('--memory', default='512', help='memory')
@click.option('--service', default='', help='service to start')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def init(box, hostname, ip_address, interface, memory, service, debug):
    """Initializes a new Vagrantfile"""

    home = expanduser("~")

    template = Template("""
Vagrant.configure("2") do |config|

  config.vm.box = "{{ box }}"
  config.vm.box_url = "file://{{ home }}/.vagrant_boxes/{{ box }}/package.box"

  config.vm.network "public_network", ip: "{{ ip_address }}", bridge: "{{ interface }}"
  {% if service|length %}
  config.vm.provision "shell",
    run: "always",
    inline: "sleep 60; systemctl start {{ service }}"
  {% endif %}
  config.vm.provider "virtualbox" do |vb|
    vb.name   = "{{ hostname }}"
    vb.memory = "{{ memory }}"
  end

  config.vm.hostname          = "{{ hostname }}"
  config.ssh.insert_key       = false
  config.ssh.private_key_path = ['~/.vagrant.d/insecure_private_key', '~/.ssh/id_rsa']
  config.vm.provision "file", source: "~/.ssh/id_rsa.pub", destination: "~/.ssh/authorized_keys"

end""")

    output = template.render(
        box=box,
        home=home,
        hostname=hostname,
        memory=memory,
        ip_address=ip_address,
        interface=interface,
        service=service
    )
    f = open('./Vagrantfile', 'w+')
    f.write(output)
    f.close()
    print(output)


root.add_command(version)
root.add_command(instance)
root.add_command(init)


def main():
    root()