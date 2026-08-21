#!/usr/bin/env bash

STATE_FILE="${XDG_RUNTIME_DIR:-/tmp}/touchpad-enabled"

if [[ ! -f "$STATE_FILE" || "$(cat "$STATE_FILE")" == "true" ]]; then
	echo true
else
	echo false
fi
