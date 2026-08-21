#!/bin/bash
# Check for system updates and return JSON
count=$(pacman -Qu 2>/dev/null | wc -l | tr -d ' ')
if [ "$count" -gt 0 ]; then
    echo "{\"text\":\"$count\", \"alt\":\"$count\", \"class\":\"green\"}"
else
    echo "{\"text\":\"0\", \"alt\":\"0\", \"class\":\"green\"}"
fi
