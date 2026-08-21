#!/bin/bash
case "$1" in
    area)
        grimblast --notify copy area
        ;;
    screen)
        grimblast --notify copy screen
        ;;
    active)
        grimblast --notify copysave active
        ;;
    *)
        echo "Usage: $0 {area|screen|active}"
        exit 1
        ;;
esac
