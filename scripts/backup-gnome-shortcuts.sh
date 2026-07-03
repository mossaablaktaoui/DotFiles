#!/usr/bin/env bash

set -e

DEST="$HOME/DotFiles/.config/gnome-dconf"
mkdir -p "$DEST"

dconf dump /org/gnome/settings-daemon/plugins/media-keys/ >"$DEST/media-keys.dconf"
dconf dump /org/gnome/desktop/wm/keybindings/ >"$DEST/wm-keybindings.dconf"
dconf dump /org/gnome/shell/keybindings/ >"$DEST/shell-keybindings.dconf"
dconf dump /org/gnome/mutter/keybindings/ >"$DEST/mutter-keybindings.dconf"

echo "GNOME shortcuts exported to $DEST"
