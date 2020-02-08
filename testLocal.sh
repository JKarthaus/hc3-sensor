#!/bin/bash

echo "Local testing the great Heating Control ds18b20Pusher"

export RABBIT_MQ_HOST=192.168.2.118
export RABBIT_MQ_EXCHANGE=hc-ds18b20

python3 ds18b20Pusher.py

