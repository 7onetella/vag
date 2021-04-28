# vag
vag is a command line utility tool for vagrant, docker and [builder](https://github.com/7onetella/containers/tree/master/builder)

## Documentation
[read the docs](https://vag.readthedocs.io/en/latest/index.html)

## Installation
```bash
$ pip install vag
```

## List of top level commands
```bash
$ vag
Usage: vag [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  build     Builds vagrant box
  clean     Cleans up vagrant build, terminates vagrant instance etc
  docker    Docker automation
  init      Creates a new Vagrantfile
  instance  Vagrant Instance Automation
  push      Publishes vagrant box to target environment
  ssh       SSH to vagrant test Vagrant instance
  test      Start a test Vagrant instance
  version   Prints version
```

## Development
local vag installation
```bash
$ rm -rf dist/*
$ poetry install
$ poetry build
$ pip uninstall -y vag
$ pip install dist/*.whl
```

edit and run 
```bash
$ poetry run vag vagrant list
```

