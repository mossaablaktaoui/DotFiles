#!/usr/bin/env bash

set -e

DEST="$HOME/.dotfiles/home/.local/share/gnome-shell"
mkdir -p "$DEST"

dconf dump /org/gnome/shell/extensions/tilingshell/ >"$DEST/tilingshell-dconf-settings.ini"

echo "Tiling Shell settings exported to $DEST"
