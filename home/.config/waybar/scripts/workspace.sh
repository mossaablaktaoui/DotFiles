#!/usr/bin/env bash

workspace="$1"

hyprctl eval "hl.dispatch(hl.dsp.focus({ workspace = \"$workspace\" }))"
