#!/bin/bash -e
#set -x

export NOMAD_ADDR=http://nomad.7onetella.net:4646
nomad run $1