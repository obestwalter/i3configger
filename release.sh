#!/usr/bin/env bash

set -e

if [[ "$(git diff --shortstat 2> /dev/null | tail -n1)" != "" ]]; then
    echo "$(git diff)"
    echo "REPO IS DIRTY!"
    exit 1
fi

python -c "import pypandoc"  # crash early if this is not installed
git tag "$1"
python setup.py sdist upload
git push --tags
echo "SUCCESS: released $(git describe --tags $(git rev-list --tags --max-count=1))"
