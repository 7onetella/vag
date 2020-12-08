import click
import os
import sys
from os.path import expanduser
from vag import __version__
from vag.console.commands.instance import instance
from jinja2 import Template
from vag.utils import exec

@click.group()
def root():
    pass


@root.command()
def version():
    """Prints version"""
    
    print(__version__)


@root.command()
@click.argument('box', default='7onetella/ubuntu-20.04', metavar='<box>')
@click.option('--hostname', default='', metavar='<hostname>')
@click.option('--ip_address', default='', metavar='<ip_address>')
@click.option('--interface', default='', help='network interface')
@click.option('--memory', default='512', help='memory')
@click.option('--service', default='', help='service to start')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def init(box, hostname, ip_address, interface, memory, service, debug):
    """Initializes a new Vagrantfile"""

    home = expanduser("~")

    # if not hostname:
    #   cwd = os.getcwd()
    #   current_folder_name = cwd[cwd.rfind('/')+1:]
    #   hostname = current_folder_name

    template = Template("""
Vagrant.configure("2") do |config|

  config.vm.box = "{{ box }}"
  config.vm.box_url = "file://{{ home }}/.vagrant_boxes/{{ box }}/package.box"{% if ip_address|length %}
  config.vm.network "public_network", ip: "{{ ip_address }}", bridge: "{{ interface }}"
  {% endif %}{% if service|length %}
  config.vm.provision "shell",
    run: "always",
    inline: "sleep 60; systemctl start {{ service }}"
  {% endif %}{% if hostname|length %}
  config.vm.provider "virtualbox" do |vb|
    vb.name   = "{{ hostname }}"{% if memory|length %}
    vb.memory = "{{ memory }}"{% endif %}
  end
  
  config.vm.hostname          = "{{ hostname }}"{% endif %}

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

    if debug:
        print(output)


@root.command()
@click.argument('box', default='', metavar='<box>')
@click.option('--base', default='7onetella/ubuntu-20.04', metavar='<base>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def build(box, base, debug):
    """Builds vagrant box"""

    organization = box[:box.rfind('/')]
    box_name = box[box.rfind('/')+1:box.rfind(':')]
    version = box[box.rfind(':') + 1:]

    template = Template("""
{
  "builders": [
    {
      "box_name"    : "{{ box }}",
      "output_dir"  : "/tmp/vagrant/build/{{ organization }}/{{ box_name }}",
      "box_version" : "{{ version }}",      
      "communicator": "ssh",
      "source_path" : "{{ base }}",
      "provider"    : "virtualbox",
      "skip_add"    : true,
      "type"        : "vagrant"
    }
  ],
  "provisioners": [
    {
      "ansible_env_vars": [ "ANSIBLE_STDOUT_CALLBACK=debug" ],
      "extra_arguments" : [ "--extra-vars", "target=default user=vagrant ansible_os_family=Debian" ],
      "type"            : "ansible",
      "playbook_file"   : "{{ box_name }}.yml",
      "user"            : "vagrant"
    }
  ]       
}""")

    try:
        os.makedirs(f'/tmp/vagrant/template/{organization}')
    except OSError:
        # do nothing
        pass

    output = template.render(
        box=box,
        base=base,
        box_name=box_name,
        organization=organization,
        version=version
    )
    template_path = f'/tmp/vagrant/template/{organization}/{box_name}.json'
    f = open(template_path, 'w+')
    f.write(output)
    f.close()
    if debug:
        print(output)

    script_path = exec.get_script_path(f'build/box.sh clean {organization} {box_name}')
    returncode, lines = exec.run(script_path, False)
    if returncode != 0:
        sys.exit(1)

    script_path = exec.get_script_path(f'build/box.sh build {template_path}')
    returncode, lines = exec.run(script_path, False)
    if returncode != 0:
        sys.exit(1)


@root.command()
@click.argument('box', default='', metavar='<box>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def push(box, debug):
    """Pushes vagrant box"""

    organization = box[:box.rfind('/')]
    box_name = box[box.rfind('/')+1:box.rfind(':')]
    version = box[box.rfind(':') + 1:]

    script_path = exec.get_script_path(f'build/box.sh push {organization} {box_name} {version}')
    returncode, lines = exec.run(script_path, False)
    if returncode != 0:
        sys.exit(1)


@root.command()
@click.argument('box', default='', metavar='<box>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def test(box, debug):
    """Tests vagrant box"""

    organization = box[:box.rfind('/')]
    box_name = box[box.rfind('/')+1:box.rfind(':')]
    version = box[box.rfind(':') + 1:]

    script_path = exec.get_script_path(f'build/box.sh test {organization} {box_name}')
    returncode, lines = exec.run(script_path, False)
    if returncode != 0:
        sys.exit(1)


root.add_command(version)
root.add_command(instance)
root.add_command(init)
root.add_command(build)
root.add_command(push)
root.add_command(test)


def main():
    root()