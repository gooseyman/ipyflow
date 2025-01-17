#!/usr/bin/env zsh

set -e  # just use set -e while we source nvm
source $HOME/.nvm/nvm.sh;
nvm use default

# ref: https://vaneyckt.io/posts/safer_bash_scripts_with_set_euxo_pipefail/
set -euxo pipefail

mkdir -p ./core/ipyflow/resources/labextension
mkdir -p ./core/ipyflow/resources/nbextension
pushd ./frontend/labextension
# install will call prepare script, which also builds
npm install
popd
pushd ./frontend/nbextension
# install will call prepare script, which also builds
npm install
popd
cp ./frontend/labextension/install.json ./core/ipyflow/resources/labextension
cp ./frontend/nbextension/ipyflow.json ./core/ipyflow/resources/nbextension
pushd ./core
python -m build
popd
python setup.py sdist bdist_wheel --universal
