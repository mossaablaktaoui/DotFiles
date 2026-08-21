#!/usr/bin/env bash

mkdir -p "$HOME/Pictures/Screenshots"

swaync-client -cp
sleep 0.2

grim -g "$(slurp)" - | tee \
	"$HOME/Pictures/Screenshots/$(date +'%Y-%m-%d_%H-%M-%S').png" |
	wl-copy
