#!/bin/bash

if [ -z "$*" ]; then echo "Usage: ./get-certs.sh DATABASE_FILE"; exit 0; fi
RESULT=$(expect - << EOF
spawn $(pwd)/manage.py $1
sleep 1
expect "Choice: "
sleep 1
send "1\n"
sleep 1
expect "\n" 
EOF
)
echo "$RESULT" | tail -n +13 | head -n -11 > certlist.txt
