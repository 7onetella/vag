

init
----
Sub command that creates a new Vagrantfile

.. code-block:: bash

    usage:
        vag init <box> <hostname> <ip_address>

    flags:
        --interface  network interface
        --hostname   vm hostname
        --ip_address ip address to bind the interface to
        --memory     memory
        --service    service to start
        --debug      debug this command

    examples:

        $ vag 7onetella/ubuntu-20.04 web-server 192.168.0.50

        Vagrant.configure("2") do |config|

          config.vm.box = "7onetella/ubuntu-20.04"
          config.vm.box_url = "file:///Users/user1/.vagrant_boxes/7onetella/ubuntu-20.04/package.box"

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
