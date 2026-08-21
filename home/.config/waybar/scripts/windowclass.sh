#!/bin/bash
active=$(hyprctl activewindow -j 2>/dev/null)
[ "$active" = "null" ] || [ -z "$active" ] && echo "" && exit
class=$(echo "$active" | python3 -c "import sys,json; print(json.load(sys.stdin).get('class',''))" 2>/dev/null)
[ -z "$class" ] && echo "" || echo "$class"
