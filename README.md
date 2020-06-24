# vag
vag is a command line utility tool for vagrant

## Github repo
[vag](https://github.com/7onetella/vag)

## Documentation
[read the docs](https://vag.readthedocs.io/en/latest/index.html)

## Installation
```bash
$ pip install vag
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
$ poetry run vag instance list
```

