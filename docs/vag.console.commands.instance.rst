instance
********
Command group for instance automation


list
----
Sub command lists all running vagrant instances

.. code-block:: bash

    usage:
        vag instance list

    flags:
        --debug debug this command

    examples:

        $ vag instance list

        name   : web-server
        shared : /Users/user1/vms/vm1
        os     : Ubuntu_64
        ip     : 192.168.0.50
        memory : 512

        name   : api-server
        shared : /Users/user1/vms/vm2
        os     : Ubuntu_64
        ip     : 192.168.0.51
        memory : 512
