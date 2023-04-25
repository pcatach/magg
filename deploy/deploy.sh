#!/bin/bash
mv /tmp/config.json /config.json
sudo apt update
sudo apt install -y python3-venv
python3 -m venv /env
/env/bin/pip install --upgrade pip
/env/bin/pip install /tmp/magg-1.0.0.tar.gz

# test that it works on deployment
/env/bin/python -m magg --renew --mail --config=/config.json >> /var/log/magg.log 2>&1

# run every Wednesday at 15:30
echo "30 15 * * 3 /env/bin/python -m magg --renew --mail --config=/config.json >> /var/log/magg.log 2>&1" | crontab -

