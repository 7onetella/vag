#!/bin/bash

rm -rf dist/*
poetry install
poetry build
pip uninstall -y vag
pip install dist/*.whl
