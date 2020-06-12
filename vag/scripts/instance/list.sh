#!/bin/bash -e

user=$1
host=$2
if [[ ${3} = "--debug" ]]; then
    set -x
fi

ssh "${user}"@"${host}" "ps -ef | grep VBoxHeadless | grep -v ps | awk '{ print \$10 }'"