#!/bin/bash
set -x

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

# Setup sudo to allow no-password sudo for "magg" group and adding "magg" user
sudo groupadd -r magg
sudo useradd -s /bin/bash -d /home/magg -m -g magg magg
sudo cp /etc/sudoers /etc/sudoers.orig
echo "magg  ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/magg
sudo chown -R magg /opt/magg

# Installing SSH key
sudo -i -u magg bash << EOF
mkdir -p /home/magg/.ssh
chmod 700 /home/magg/.ssh  
cp /tmp/aws-magg.pub /home/magg/.ssh/authorized_keys
chmod 600 /home/magg/.ssh/authorized_keys
EOF

# run every Wednesday at 15:30
echo "30 15 * * 3 /opt/magg/env/bin/python -m magg --renew --mail --mail-from=$MAIL_FROM --mail-to=$MAIL_TO >> /var/log/magg.log 2>&1" | crontab -

