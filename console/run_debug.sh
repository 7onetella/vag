#!/bin/bash

# export FLASK_APP=console/app

export FLASK_ENV=development

poetry run python3 ./app.py --debug=True