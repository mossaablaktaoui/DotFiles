#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
status=0

python3 "$ROOT/liquid-glass/build_palettes.py"
python3 -m json.tool "$ROOT/liquid-glass/tokens.json" >/dev/null

echo "JSON and generated palettes: OK"

if command -v rofi >/dev/null 2>&1; then
    rofi -no-config -theme "$ROOT/rofi/launcher.rasi" -dump-theme >/dev/null || status=1
    rofi -no-config -theme "$ROOT/rofi/power-menu.rasi" -dump-theme >/dev/null || status=1
    echo "Rofi parsing: checked"
else
    echo "Rofi parsing: skipped (rofi is not installed)"
fi

if command -v waybar >/dev/null 2>&1; then
    echo "Waybar is installed; restart/reload it to let GTK report CSS errors."
else
    echo "Waybar runtime check: skipped (waybar is not installed)"
fi

if command -v swaync >/dev/null 2>&1; then
    echo "SwayNC is installed; run 'swaync-client -rs' to let GTK report CSS errors."
else
    echo "SwayNC runtime check: skipped (swaync is not installed)"
fi

exit "$status"
