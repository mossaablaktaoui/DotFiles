#!/usr/bin/env bash

if swaync-client -D | grep -q true; then
	echo true
else
	echo false
fi
