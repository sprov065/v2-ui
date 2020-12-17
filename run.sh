#!/usr/bin/env bash

git pull

source venv/bin/activate

systemctl stop v2-ui

python v2-ui.py "$@"
