#!/bin/bash
# ML4W Wallpaper + Color Generator
SCRIPT_DIR="$HOME/.config/hypr/scripts"
WALLPAPER="$1"

if [ -z "$WALLPAPER" ]; then
    # Restore from cache
    if [ -f "$HOME/.cache/ml4w/hyprland-dotfiles/current_wallpaper" ]; then
        WALLPAPER=$(cat "$HOME/.cache/ml4w/hyprland-dotfiles/current_wallpaper")
    fi
    if [ ! -f "$WALLPAPER" ]; then
        exit 1
    fi
fi

if [ ! -f "$WALLPAPER" ]; then
    echo "Wallpaper not found: $WALLPAPER"
    exit 1
fi

# Generate colors from wallpaper
python3 "$SCRIPT_DIR/ml4w-colorgen.py" "$WALLPAPER"

# Restart waybar to apply new colors
killall waybar 2>/dev/null
pkill waybar 2>/dev/null
sleep 0.5
bash "$HOME/.config/waybar/launch.sh" &
