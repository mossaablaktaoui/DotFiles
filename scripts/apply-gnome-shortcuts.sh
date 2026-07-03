#!/usr/bin/env bash

set -e

SRC="$HOME/DotFiles/.config/gnome-dconf"

dconf load /org/gnome/settings-daemon/plugins/media-keys/ <"$SRC/media-keys.dconf"
dconf load /org/gnome/desktop/wm/keybindings/ <"$SRC/wm-keybindings.dconf"
dconf load /org/gnome/shell/keybindings/ <"$SRC/shell-keybindings.dconf"
dconf load /org/gnome/mutter/keybindings/ <"$SRC/mutter-keybindings.dconf"

echo "GNOME shortcuts restored"
