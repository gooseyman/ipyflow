#!/usr/bin/env bash

set -e  # just use set -e while we source nvm
source $HOME/.nvm/nvm.sh;
nvm use default

# ref: https://vaneyckt.io/posts/safer_bash_scripts_with_set_euxo_pipefail/
set -euxo pipefail

if ! git diff-index --quiet HEAD --; then
    echo "dirty working tree; please clean or commit changes"
    exit 1
fi

if ! git describe --exact-match --tags HEAD > /dev/null; then
    echo "current revision not tagged; please deploy from a tagged revision"
    exit 1
fi

if [ ! -f ./core/ipyflow/resources/nbextension/index.js ]; then
    echo "resources/nbextension/index.js not present; please build the nbextension with `make build` and try again"
    exit 1
fi

current="$(python -c 'import versioneer; print(versioneer.get_version())')"
[[ $? -eq 1 ]] && exit 1

latest="$(git describe --tags $(git rev-list --tags --max-count=1))"
[[ $? -eq 1 ]] && exit 1

jlab="$(python -c 'import json; print(json.loads(open("frontend/labextension/package.json").read())["version"])')"
[[ $? -eq 1 ]] && exit 1

if [[ "$current" != "$latest" ]]; then
    echo "current revision is not the latest version; please deploy from latest version"
    exit 1
fi

if [[ "$current" != "$jlab" ]]; then
    echo "current revision is not the latest version; please deploy from latest version"
    exit 1
fi

for pkg_dir in ./core .; do
    pushd $pkg_dir
    expect <<EOF
set timeout -1

spawn twine upload dist/*

expect "Enter your username:"
send -- "$(lpass show pypi.org --field=username)\r"

expect "Enter your password:"
send -- "$(lpass show pypi.org --field=password)\r"
expect
EOF
    popd
    done

pushd ./frontend/labextension
npm publish
popd

git push --tags
