#!/bin/bash
while true; do
  python3.7 /discordbot/main.py &
  wait $!
  sleep 5
done
exit