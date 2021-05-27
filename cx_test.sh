#!/bin/bash -e

clear

set -x

vag cx reset-test-data

vag cx clone-user foo bar changeme bar@example.com

vag cx get-profile bar vscode

vag cx delete-user bar

vag cx add-user baz changeme baz@example.com

vag cx add-user-repo baz git@example.com/baz/project

vag cx add-user-ide baz vscode

vag cx add-ide-runtime-install baz vscode tmux

vag cx add-ide-repo baz vscode git@example.com/baz/project

cat ~/.ssh/id_rsa | vag cx user-private-key baz

echo -n "baz user public key" | vag cx user-public-key baz

vag cx get-profile baz vscode

vag cx get-profile baz vscode | vag docker pre-build 

vag docker post-build vscode-baz-public

vag cx delete-user baz
