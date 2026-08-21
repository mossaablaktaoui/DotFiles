# Liquid Glass theme bundle

This bundle reorganizes the supplied Waybar, Rofi, and SwayNC styles around one visual token set.

## Design structure

- `liquid-glass/tokens.json` is the color source of truth.
- `liquid-glass/palette.css` is directly shared by Waybar and SwayNC through GTK CSS `@import`.
- `liquid-glass/palette.rasi` is the synchronized Rofi form of the same palette.
- `liquid-glass/build_palettes.py` regenerates both palette files after editing `tokens.json`.
- Rofi also receives reusable numeric tokens for radii, gaps, and the top/bottom glass border.
- The shared GTK target must stay compatible with Waybar’s GTK 3 stylesheet engine. GTK 3 has named colors but no browser-style numeric custom properties, so repeated radii and spacing are consolidated with grouped selectors instead of fake variables.

## Main cleanup decisions

- Unified near-duplicate values into semantic levels: panel, glass, surface, hover, pressed, border, track, fill, text, dim text, and status colors.
- Removed duplicated and contradictory SwayNC notification rules.
- Added explicit margins and padding for notification groups, group headers, grouped notifications, and regular notification rows.
- Grouped Waybar modules that share backgrounds, foregrounds, hover states, transitions, and shadows.
- Replaced duplicate Rofi border declarations with reusable Rasi metrics.
- Kept a `rofi/colors.rasi` compatibility file for other menus that still use the old variable names.

## Install

From this extracted folder:

```bash
./install.sh
```

The installer backs up existing files before replacing them.

## Manual layout

```text
~/.config/liquid-glass/
  tokens.json
  palette.css
  palette.rasi
  build_palettes.py

~/.config/waybar/style.css
~/.config/swaync/style.css
~/.config/rofi/launcher.rasi
~/.config/rofi/power-menu.rasi
~/.config/rofi/colors.rasi
```

## Change the palette later

Edit:

```text
~/.config/liquid-glass/tokens.json
```

Then regenerate and reload:

```bash
python ~/.config/liquid-glass/build_palettes.py
pkill -SIGUSR2 waybar
swaync-client -rs
```

Rofi reads the palette the next time a menu opens.

## Validation

Run:

```bash
./validate-theme.sh
```

The script validates JSON and regenerates palettes. When Rofi is installed it also asks Rofi to parse both themes.
