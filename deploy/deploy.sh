#!/bin/bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv env
./env/bin/pip install --upgrade pip
./env/bin/pip install /tmp/magg-1.0.0.tar.gz

# this is temporary
echo {} > config.json
./env/bin/python -m magg --renew