#!/bin/bash
set -e

apt-get update
apt-get install -y python3

echo "Cloud burst worker started at $(date)" > /tmp/burst_log.txt
sleep 30
echo "Cloud burst worker finished at $(date)" >> /tmp/burst_log.txt

shutdown -h now
