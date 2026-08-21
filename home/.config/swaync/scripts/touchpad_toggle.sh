#!/usr/bin/env bash

DEVICE="elan1200:00-04f3:309f-touchpad"
RUNTIME_DIR="${XDG_RUNTIME_DIR:-/tmp}"
STATE_FILE="$RUNTIME_DIR/touchpad-enabled"
LOCK_FILE="$RUNTIME_DIR/touchpad-toggle.lock"

exec 9>"$LOCK_FILE"
flock -n 9 || exit 0

notify() {
	gdbus call --session \
		--dest org.freedesktop.Notifications \
		--object-path /org/freedesktop/Notifications \
		--method org.freedesktop.Notifications.Notify \
		"Touchpad Toggle" \
		0 \
		"" \
		"Touchpad" \
		"$1" \
		"[]" \
		"{}" \
		2000 >/dev/null
}

# Missing state file means the touchpad starts enabled.
CURRENT_STATE="$(cat "$STATE_FILE" 2>/dev/null || echo true)"

if [[ "$CURRENT_STATE" == "true" ]]; then
	NEXT_STATE=false
	MESSAGE="The touchpad has been disabled."
else
	NEXT_STATE=true
	MESSAGE="The touchpad has been enabled."
fi

OUTPUT="$(
	hyprctl -i 0 eval \
		"hl.device({ name = \"$DEVICE\", enabled = $NEXT_STATE })" 2>&1
)"

if [[ "$OUTPUT" != "ok" ]]; then
	exit 1
fi

printf '%s\n' "$NEXT_STATE" >"$STATE_FILE"
notify "$MESSAGE"
