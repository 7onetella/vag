#!/bin/bash -e
if [[ ${3} = "--debug" ]]; then
    set -x
fi
ps -ef | grep VBoxHeadless | grep -v ps | awk '{ print $10 }'