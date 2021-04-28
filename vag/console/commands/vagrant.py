import sys
from os.path import expanduser
import click
from vag.utils import exec
import untangle
from jinja2 import Template
from vag.utils import exec
from vag.utils import hash_util
import os
import sys
from os.path import expanduser


@click.group()
def vagrant():
    """ Vagrant Instance Automation """
    pass


@vagrant.command()
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


@vagrant.command()
@click.argument('box', default='7onetella/ubuntu-20.04', metavar='<box>')
@click.option('--hostname', default='', metavar='<hostname>')
@click.option('--ip_address', default='', metavar='<ip_address>')
@click.option('--interface', default='', help='network interface')
@click.option('--memory', default='512', help='memory')
@click.option('--service', default='', help='service to start')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def init(box, hostname, ip_address, interface, memory, service, debug):
    """Creates a new Vagrantfile"""

    home = expanduser("~")

    # if not hostname:
    #   cwd = os.getcwd()
    #   current_folder_name = cwd[cwd.rfind('/')+1:]
    #   hostname = current_folder_name

    # config.vm.box_url = "file://{{ home }}/.vagrant/boxes/{{ box }}/package.box"

    template = Template("""
Vagrant.configure("2") do |config|

  config.vm.box = "{{ box }}"{% if ip_address|length %}
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


@vagrant.command()
@click.argument('box', default='', metavar='<box>')
@click.option('--base', default='7onetella/ubuntu-20.04', metavar='<base>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def build(box, base, debug):
    """Builds vagrant box"""

    organization = box[:box.rfind('/')]
    box_name = box[box.rfind('/')+1:box.rfind(':')]
    version_ = box[box.rfind(':') + 1:]

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
        os.makedirs(f'/tmp/vagrant/template/{organization}/{box_name}')
    except OSError:
        # do nothing
        pass

    output = template.render(
        box=box,
        base=base,
        box_name=box_name,
        organization=organization,
        version=version_
    )
    template_path = f'/tmp/vagrant/template/{organization}/{box_name}/{box_name}.json'
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


@vagrant.command()
@click.argument('box', default='', metavar='<box>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
@click.option('--skip', is_flag=True, default=False, help='skip copying the box')
def push(box, debug, skip):
    """Publishes vagrant box to target environment"""

    organization = box[:box.rfind('/')]
    box_name = box[box.rfind('/')+1:box.rfind(':')]
    version_ = box[box.rfind(':') + 1:]

    if not skip:
        print("scp-ing the box")
        script_path = exec.get_script_path(f'build/box.sh push {organization} {box_name}')
        returncode, lines = exec.run(script_path, False)
        if returncode != 0:
            sys.exit(1)

    try:
        os.makedirs(f'/tmp/vagrant/metadata/{organization}/{box_name}')
    except OSError:
        # do nothing
        pass

    metadata_template = Template("""
    {
      "description": "",
       "name": "{{ organization }}/{{ box_name }}",
       "versions": [
         {
           "providers": [
             {
              "checksum": "{{ sha1sum }}",
              "checksum_type": "sha1",
              "name": "virtualbox",
              "url": "http://tmt.7onetella.net/boxes/{{ organization }}/{{ box_name }}/package.box"
             }
           ],
           "version": "{{ version }}"
         }
       ]
    }""")
    metadata_output = metadata_template.render(
        box=box,
        organization=organization,
        box_name=box_name,
        sha1sum=hash_util.sha1sum(f'/tmp/vagrant/build/{organization}/{box_name}/package.box'),
        version=version_
    )
    metadata_json_path = f'/tmp/vagrant/metadata/{organization}/{box_name}/metadata.json'
    f = open(metadata_json_path, 'w+')
    f.write(metadata_output)
    f.close()
    if debug:
        print(metadata_output)

    print("scp-ing the metadata.json")
    script_path = exec.get_script_path(f'build/box.sh metadata {organization} {box_name}')
    returncode, lines = exec.run(script_path, False)
    if returncode != 0:
        sys.exit(1)


@vagrant.command()
@click.argument('box', default='', metavar='<box>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def test(box, debug):
    """Start a test Vagrant instance"""

    organization = box[:box.rfind('/')]
    box_name = box[box.rfind('/')+1:]

    script_path = exec.get_script_path(f'build/box.sh test {organization} {box_name}')
    returncode, lines = exec.run(script_path, False)
    if returncode != 0:
        sys.exit(1)


@vagrant.command()
@click.argument('box', default='', metavar='<box>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def ssh(box, debug):
    """SSH to vagrant test Vagrant instance"""

    organization = box[:box.rfind('/')]
    box_name = box[box.rfind('/')+1:]

    script_path = exec.get_script_path(f'build/box.sh ssh {organization} {box_name}')
    exec.fork(script_path, debug)


@vagrant.command()
@click.argument('box', default='', metavar='<box>')
@click.option('--debug', is_flag=True, default=False, help='debug this command')
def clean(box, debug):
    """Cleans up vagrant build, terminates vagrant instance etc"""

    organization = box[:box.rfind('/')]
    box_name = box[box.rfind('/')+1:]

    script_path = exec.get_script_path(f'build/box.sh clean {organization} {box_name}')
    returncode, lines = exec.run(script_path, False)
    if returncode != 0:
        sys.exit(1)

