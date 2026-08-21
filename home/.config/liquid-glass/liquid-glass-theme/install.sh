#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
STAMP="$(date +%Y%m%d-%H%M%S)"

backup_file() {
    local target="$1"
    if [[ -f "$target" ]]; then
        cp -a -- "$target" "${target}.backup-${STAMP}"
    fi
}

mkdir -p \
    "$CONFIG_HOME/liquid-glass" \
    "$CONFIG_HOME/rofi" \
    "$CONFIG_HOME/waybar" \
    "$CONFIG_HOME/swaync"

backup_file "$CONFIG_HOME/rofi/launcher.rasi"
backup_file "$CONFIG_HOME/rofi/power-menu.rasi"
backup_file "$CONFIG_HOME/rofi/colors.rasi"
backup_file "$CONFIG_HOME/waybar/style.css"
backup_file "$CONFIG_HOME/swaync/style.css"

cp -a -- "$ROOT/liquid-glass/." "$CONFIG_HOME/liquid-glass/"
cp -a -- "$ROOT/rofi/." "$CONFIG_HOME/rofi/"
cp -a -- "$ROOT/waybar/style.css" "$CONFIG_HOME/waybar/style.css"
cp -a -- "$ROOT/swaync/style.css" "$CONFIG_HOME/swaync/style.css"

printf 'Installed liquid-glass theme files.\n'
printf 'Backups, when needed, use suffix: .backup-%s\n' "$STAMP"
printf 'Reload with:\n'
printf '  pkill -SIGUSR2 waybar\n'
printf '  swaync-client -rs\n'
