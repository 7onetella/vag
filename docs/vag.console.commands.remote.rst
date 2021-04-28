remote
******
Command group for remote builder automation

build
-----
Sub command runs build in remote builder.

.. code-block:: bash

    usage:
        vag remote build <repo> <branch>

    flags:
        --debug      debug this command

    examples:
        vag remote build users master

deploy
------
Sub command runs deploy in remote builder.

.. code-block:: bash

    usage:
        vag remote deploy <repo> <stage>

    flags:
        --debug      debug this command

    examples:
        vag remote deploy users dev

ssh
---
Sub command ssh to remote builder.

.. code-block:: bash

    usage:
        vag remote ssh

    flags:
        --debug      debug this command

    examples:
        vag remote ssh
