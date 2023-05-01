#!/bin/bash
set -x

# Install necessary dependencies
sudo apt update -y
sudo apt upgrade -y
sudo apt install -y python3.10-venv

# Install python package
sudo mkdir /opt/magg
sudo chown -R ubuntu /opt/magg
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts
git clone git@github.com:pcatach/magg.git /opt/magg
python3 -m venv /opt/magg/env
/opt/magg/env/bin/pip install --upgrade pip
/opt/magg/env/bin/pip install -r /opt/magg/requirements.txt

# Setup sudo to allow no-password sudo for "magg" group and adding "magg" user
sudo groupadd -r magg
sudo useradd -s /bin/bash -g magg magg
sudo cp /etc/sudoers /etc/sudoers.orig
echo "magg  ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/magg

# Installing SSH key
mkdir -p /home/magg/.ssh
chmod 700 /home/magg/.ssh  
cp /tmp/aws-magg.pub /home/magg/.ssh/authorized_keys
chmod 600 /home/magg/.ssh/authorized_keys
chown -R magg /home/magg/.ssh
chown -R magg /opt/magg

# run every Wednesday at 15:30
echo "30 15 * * 3 /opt/magg/env/bin/python -m magg --renew --mail --mail-from=$MAIL_FROM --mail-to=$MAIL_TO >> /var/log/magg.log 2>&1" | crontab -

