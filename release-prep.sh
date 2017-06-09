#!/usr/bin/env bash

set -e

pip install pypandoc
python i3configger/util.py
git add CHANGELOG.md
git add docs/_pypi/*
git commit -m "prep release"
git push
