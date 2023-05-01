#!/bin/bash
set -x

# Installing SSH key
sudo -i -u ubuntu bash << EOF
cp /tmp/aws-magg.pub /home/ubuntu/.ssh/authorized_keys
chmod 600 /home/ubuntu/.ssh/authorized_keys
EOF

# Install python package
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install -y python3.10-venv
sudo mkdir /opt/magg
sudo chown -R ubuntu /opt/magg
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts
git clone git@github.com:pcatach/magg.git /opt/magg
python3 -m venv /opt/magg/env
/opt/magg/env/bin/pip install --upgrade pip
/opt/magg/env/bin/pip install -r /opt/magg/requirements.txt

# Setup var directory
sudo mkdir /var/magg
sudo chown -R ubuntu /var/magg