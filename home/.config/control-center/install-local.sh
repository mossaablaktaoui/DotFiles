#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/moss-control-center"
BIN_DIR="$HOME/.local/bin"

mkdir -p "$APP_DIR" "$BIN_DIR"
rm -rf "$APP_DIR/common" "$APP_DIR/services"
mkdir -p "$APP_DIR"

cp -r common services "$APP_DIR/"
install -Dm755 wifi.py "$APP_DIR/wifi.py"
install -Dm755 bluetooth.py "$APP_DIR/bluetooth.py"
install -Dm755 hotspot.py "$APP_DIR/hotspot.py"
install -Dm755 sound.py "$APP_DIR/sound.py"

for name in wifi bluetooth hotspot sound; do
    install -Dm755 "run-${name}.sh" "$APP_DIR/run-${name}.sh"

    cat > "$BIN_DIR/moss-${name}" <<EOF
#!/usr/bin/env bash
exec "$APP_DIR/run-${name}.sh"
EOF

    chmod +x "$BIN_DIR/moss-${name}"
done

printf 'Installed launchers:\n'
printf '  %s\n' \
    "$BIN_DIR/moss-wifi" \
    "$BIN_DIR/moss-bluetooth" \
    "$BIN_DIR/moss-hotspot" \
    "$BIN_DIR/moss-sound"
printf '\nMake sure ~/.local/bin is in PATH.\n'
