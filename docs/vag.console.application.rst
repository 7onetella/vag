

init
****
Sub command that creates a new Vagrantfile

.. code-block:: bash

    usage:
        vag init <box>

    flags:
        --interface  network interface
        --hostname   vm hostname
        --ip_address ip address to bind the interface to
        --interface  network interface name
        --memory     memory
        --service    service to start
        --debug      debug this command

    examples:

        $ vag 7onetella/ubuntu-20.04 --hostname web-server --ip_address 192.168.0.50 --interface eno1

        Vagrant.configure("2") do |config|

          config.vm.box = "7onetella/ubuntu-20.04"

          config.vm.network "public_network", ip: "192.168.0.50", bridge: "eno1"

          config.vm.provider "virtualbox" do |vb|
            vb.name   = "web-server"
            vb.memory = "512"
          end

          config.vm.hostname = "web-server"
          config.ssh.insert_key = false # 1
          config.ssh.private_key_path = ['~/.vagrant.d/insecure_private_key', '~/.ssh/id_rsa'] # 2
          config.vm.provision "file", source: "~/.ssh/id_rsa.pub", destination: "~/.ssh/authorized_keys" # 3

        end

build
*****
Sub command that builds vagrant box. This internally uses Hashcorp's `Packer <https://www.packer.io/>`_ to create vagrant
box. Packer expects a template file to be specified. The template file describes how vagrant box is to be built. This tool
generates the template file for you. The required implicit input is `Ansible <https://www.packer.io/docs/provisioners/ansible>`_ playbook.
In your terminal, change directory to where your Ansible playbook reside and execute this command.

.. code-block:: bash

    usage:
        vag build <box>

    flags:
        --base       <base>
        --debug      debug this command

    examples:
        vag build 7onetella/nomad-node:1.0.0

<box> is made of three parts. [organization] / [box name] : [version].
[box name].yml should be the name of your playbook. For example, nomad-nomad.yml should be in the current directory.
