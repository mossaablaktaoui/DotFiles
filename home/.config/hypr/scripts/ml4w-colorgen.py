#!/usr/bin/env python3
"""
ML4W Color Generator
Extracts colors from a wallpaper and generates CSS/rasi theme files.
"""

import json
import os
import subprocess
import sys
from collections import Counter

try:
    from PIL import Image
except ImportError:
    print("ERROR: Python Pillow not installed")
    sys.exit(1)

HOME = os.path.expanduser("~")
CACHE_DIR = os.path.join(HOME, ".cache", "ml4w", "hyprland-dotfiles")
CONFIG_DIR = os.path.join(HOME, ".config")
WALLPAPER_CACHE = os.path.join(CACHE_DIR, "current_wallpaper")
COLORS_CSS = os.path.join(CONFIG_DIR, "waybar", "colors.css")
COLORS_RASI = os.path.join(CONFIG_DIR, "rofi", "colors.rasi")
WALLPAPER_RASI = os.path.join(CACHE_DIR, "current_wallpaper.rasi")


def get_dominant_colors(image_path, n_colors=8):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((150, 100))
    pixels = list(img.getdata())
    
    # Simple color quantization
    quantized = []
    for r, g, b in pixels:
        quantized.append((r // 32 * 32, g // 32 * 32, b // 32 * 32))
    
    counter = Counter(quantized)
    most_common = counter.most_common(n_colors)
    
    return [color for color, count in most_common]


def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def luminance(r, g, b):
    return 0.299 * r + 0.587 * g + 0.114 * b


def is_dark(r, g, b):
    return luminance(r, g, b) < 128


def adjust_brightness(r, g, b, factor):
    return (
        min(255, max(0, int(r * factor))),
        min(255, max(0, int(g * factor))),
        min(255, max(0, int(b * factor))),
    )


def mix_colors(c1, c2, ratio):
    r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
    g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
    b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
    return (r, g, b)


def generate_palette(colors):
    if not colors:
        colors = [(30, 30, 46), (137, 180, 250), (205, 214, 244)]
    
    bg_color = colors[0]
    dark = is_dark(*bg_color)
    
    # Sort colors by luminance for predictable ordering
    sorted_colors = sorted(colors, key=lambda c: luminance(*c))
    
    # Primary: most saturated/vibrant color (usually not the darkest)
    non_dark = [c for c in sorted_colors if not is_dark(*c)]
    if non_dark:
        primary = non_dark[0]
    else:
        primary = sorted_colors[-1]
    
    # Secondary: second most prominent
    secondary = sorted_colors[-2] if len(sorted_colors) > 1 else primary
    
    # Surface background
    surface = bg_color
    
    # Text color: opposite of background
    if dark:
        text = (205, 214, 244)  # light text
        subtext = (166, 173, 200)
        surface_light = adjust_brightness(*bg_color, 1.1)
        surface_dark = adjust_brightness(*bg_color, 0.9)
    else:
        text = (30, 30, 46)  # dark text
        subtext = (69, 71, 90)
        surface_light = adjust_brightness(*bg_color, 0.95)
        surface_dark = adjust_brightness(*bg_color, 1.05)
    
    palette = {
        "background": rgb_to_hex(*bg_color),
        "surface": rgb_to_hex(*mix_colors(bg_color, (255, 255, 255), 0.08 if dark else -0.08)),
        "surface0": rgb_to_hex(*mix_colors(bg_color, (255, 255, 255), 0.15 if dark else -0.15)),
        "surface1": rgb_to_hex(*mix_colors(bg_color, (255, 255, 255), 0.25 if dark else -0.25)),
        "surface2": rgb_to_hex(*mix_colors(bg_color, (255, 255, 255), 0.35 if dark else -0.35)),
        "overlay0": rgb_to_hex(*mix_colors(bg_color, (255, 255, 255), 0.45 if dark else -0.45)),
        "primary": rgb_to_hex(*primary),
        "secondary": rgb_to_hex(*secondary),
        "text": rgb_to_hex(*text),
        "subtext": rgb_to_hex(*subtext),
        "error": rgb_to_hex(243, 139, 168),
        "surface_light": rgb_to_hex(*surface_light),
        "surface_dark": rgb_to_hex(*surface_dark),
    }
    
    return palette


def write_waybar_colors(palette):
    css = f"""/*
* CSS Colors - Auto-generated from wallpaper
*/
@define-color background {palette['background']};

@define-color surface {palette['surface']};
@define-color surface0 {palette['surface0']};
@define-color surface1 {palette['surface1']};
@define-color surface2 {palette['surface2']};
@define-color overlay0 {palette['overlay0']};

@define-color primary {palette['primary']};
@define-color secondary {palette['secondary']};
@define-color text {palette['text']};
@define-color subtext {palette['subtext']};
@define-color error {palette['error']};

@define-color on_background {palette['text']};
@define-color on_surface {palette['text']};
@define-color on_surface_variant {palette['subtext']};
@define-color on_primary {palette['background']};
@define-color on_secondary {palette['background']};
@define-color on_error {palette['background']};

@define-color backgroundlight {palette['surface']};
@define-color backgrounddark {palette['surface']};
@define-color workspacesbackground1 {palette['surface']};
@define-color workspacesbackground2 {palette['surface0']};
@define-color bordercolor {palette['primary']};
@define-color textcolor1 {palette['text']};
@define-color textcolor2 {palette['background']};
@define-color textcolor3 {palette['text']};
@define-color iconcolor {palette['text']};

@define-color blur_background {palette['background']}33;
@define-color blur_background8 {palette['background']}CC;

@define-color error_container #93000a;
@define-color inverse_on_surface {palette['text']};
@define-color inverse_primary {palette['primary']};
@define-color inverse_surface {palette['background']};
@define-color on_error_container {palette['error']};
@define-color on_primary_container {palette['subtext']};
@define-color on_primary_fixed {palette['background']};
@define-color on_primary_fixed_variant {palette['surface0']};
@define-color on_secondary_container {palette['subtext']};
@define-color on_secondary_fixed {palette['background']};
@define-color on_secondary_fixed_variant {palette['surface1']};
@define-color on_tertiary {palette['background']};
@define-color on_tertiary_container {palette['subtext']};
@define-color on_tertiary_fixed {palette['background']};
@define-color on_tertiary_fixed_variant {palette['surface2']};
@define-color outline {palette['overlay0']};
@define-color outline_variant {palette['surface1']};
@define-color scrim #000000;
@define-color shadow #000000;
@define-color source_color {palette['primary']};
@define-color surface_bright {palette['surface0']};
@define-color surface_container {palette['surface']};
@define-color surface_container_high {palette['surface0']};
@define-color surface_container_highest {palette['surface1']};
@define-color surface_container_low {palette['background']};
@define-color surface_container_lowest {palette['background']};
@define-color surface_dim {palette['background']};
@define-color surface_tint {palette['primary']};
@define-color surface_variant {palette['surface1']};
@define-color tertiary {palette['secondary']};
@define-color tertiary_container {palette['surface2']};
@define-color tertiary_fixed {palette['subtext']};
@define-color tertiary_fixed_dim {palette['secondary']};
"""
    os.makedirs(os.path.dirname(COLORS_CSS), exist_ok=True)
    with open(COLORS_CSS, "w") as f:
        f.write(css)
    print(f"  -> Written {COLORS_CSS}")


def write_rofi_colors(palette):
    rasi = f"""* {{
    background: {palette['background']};
    surface: {palette['surface']};
    surface0: {palette['surface0']};
    surface1: {palette['surface1']};
    overlay0: {palette['overlay0']};
    blue: {palette['primary']};
    primary: {palette['primary']};
    on-primary: {palette['background']};
    on-surface: {palette['text']};
    on-surface-variant: {palette['subtext']};
    text: {palette['text']};
    subtext0: {palette['subtext']};
    border-color: @surface1;
    border-width: 2px;
    border-radius: 16px;
    background-image: none;
    current-image: none;
}}
"""
    os.makedirs(os.path.dirname(COLORS_RASI), exist_ok=True)
    with open(COLORS_RASI, "w") as f:
        f.write(rasi)
    print(f"  -> Written {COLORS_RASI}")


def write_wallpaper_rasi(image_path):
    rasi = f"""* {{
    current-image: url("{image_path}");
}}
"""
    os.makedirs(os.path.dirname(WALLPAPER_RASI), exist_ok=True)
    with open(WALLPAPER_RASI, "w") as f:
        f.write(rasi)
    print(f"  -> Written {WALLPAPER_RASI}")


def set_wallpaper_swaybg(image_path):
    subprocess.run(["killall", "swaybg"], capture_output=True)
    subprocess.Popen(["swaybg", "-i", image_path, "-m", "fill"])


def set_wallpaper_hyprpaper(image_path):
    subprocess.run(["killall", "hyprpaper"], capture_output=True)
    config = f"preload = {image_path}\nwallpaper = eDP-1,{image_path}\n"
    config_path = os.path.join(HOME, ".config", "hypr", "hyprpaper.conf")
    with open(config_path, "w") as f:
        f.write(config)
    subprocess.Popen(["hyprpaper"])


def main():
    if len(sys.argv) < 2:
        print("Usage: ml4w-colorgen.py <wallpaper_path>")
        print("       ml4w-colorgen.py --restore")
        return 1
    
    if sys.argv[1] == "--restore":
        if os.path.exists(WALLPAPER_CACHE):
            with open(WALLPAPER_CACHE) as f:
                wallpaper = f.read().strip()
            if os.path.exists(wallpaper):
                generate_and_apply(wallpaper)
                return 0
        print("No cached wallpaper found")
        return 1
    
    wallpaper = sys.argv[1]
    if not os.path.exists(wallpaper):
        print(f"Wallpaper not found: {wallpaper}")
        return 1
    
    generate_and_apply(wallpaper)
    return 0


def generate_and_apply(wallpaper):
    print(f"Generating colors from: {wallpaper}")
    
    # Extract colors
    colors = get_dominant_colors(wallpaper)
    
    # Generate palette
    palette = generate_palette(colors)
    
    print(f"  Background: {palette['background']}")
    print(f"  Primary:    {palette['primary']}")
    print(f"  Text:       {palette['text']}")
    
    # Write color files
    write_waybar_colors(palette)
    write_rofi_colors(palette)
    write_wallpaper_rasi(wallpaper)
    
    # Cache current wallpaper
    os.makedirs(os.path.dirname(WALLPAPER_CACHE), exist_ok=True)
    with open(WALLPAPER_CACHE, "w") as f:
        f.write(wallpaper)
    
    # Set wallpaper
    if shutil.which("hyprpaper"):
        set_wallpaper_hyprpaper(wallpaper)
    elif shutil.which("swaybg"):
        set_wallpaper_swaybg(wallpaper)

    print("Done! Colors regenerated.")


if __name__ == "__main__":
    import shutil
    main()
