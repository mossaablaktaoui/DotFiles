#!/usr/bin/env bash

wall="$1"

# Generate colors
wallust run "$wall"

# Reload Waybar
pkill waybar
waybar &

# Reload Hyprland (for border colors later)
hyprctl reload

# Reload Dunst if it's running
pkill dunst
dunst &
