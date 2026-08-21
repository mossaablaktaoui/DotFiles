#!/usr/bin/env bash

if wpctl get-volume @DEFAULT_AUDIO_SOURCE@ | grep -q "MUTED"; then
	echo true
else
	echo false
fi
