#!/usr/bin/env bash

set -e

SRC="$HOME/.dotfiles/home/.local/share/gnome-shell"

dconf load /org/gnome/shell/extensions/tilingshell/ <"$SRC/tilingshell-dconf-settings.ini"

echo "Tiling Shell settings restored"
