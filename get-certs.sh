#!/bin/bash

RESULT=$(expect - << EOF
spawn $(pwd)/manage.py certs.db
sleep 1
expect "Choice: "
sleep 1
send "1\n"
sleep 1
expect "\n" 
EOF
)
echo "$RESULT" | tail -n +13 | head -n -11 > certlist.txt
