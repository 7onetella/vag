docker
******
Command group for docker automation

deploy
------
Sub command deploys docker image in nomad environment.

.. code-block:: bash

    usage:
        vag docker deploy <service-name>

    flags:
        --debug      debug this command

    examples:
        vag docker deploy builder-dev:1.0.0

