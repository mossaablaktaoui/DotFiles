#!/bin/bash
active=$(hyprctl activewindow -j 2>/dev/null)
if [ "$active" = "null" ] || [ -z "$active" ]; then
    echo ""
    exit
fi
class=$(echo "$active" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('class',''))" 2>/dev/null || echo "")
if [ -z "$class" ]; then
    echo ""
    exit
fi
case "$class" in
    kitty|wezterm|Alacritty|Foot|foot) echo "Terminal" ;;
    firefox|Firefox) echo "Firefox" ;;
    google-chrome|Google-chrome|chromium|Chromium|brave|Brave) echo "Browser" ;;
    code-oss|Code|code|Code - OSS) echo "VS Code" ;;
    thunar|Thunar|dolphin|Dolphin|nautilus|Nautilus) echo "Files" ;;
    *) echo "$class" ;;
esac
