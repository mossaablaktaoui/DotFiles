# Moss GTK Control Center

Four small GTK4/Libadwaita control windows designed for Hyprland:

- `moss-wifi`
- `moss-bluetooth`
- `moss-hotspot`
- `moss-sound`

All windows share the same frameless layout, header, spacing, typography, glass styling, asynchronous worker, and bottom settings button.

## Features

### Wi-Fi

- Power toggle in the header
- Connected SSID and signal strength
- Scrollable list of available networks
- Password subwindow and show-password toggle
- Non-blocking connection attempts
- Success notification
- GNOME Wi-Fi Settings shortcut

### Bluetooth

- Power toggle in the header
- Connected, paired, and available device groups
- Connect and disconnect paired devices
- Pair confirmation subwindow
- Non-blocking scanning and operations
- Success notifications
- GNOME Bluetooth Settings shortcut

The built-in quick pairing is intended for common JustWorks devices such as many headphones and mice. Devices requiring a PIN, passkey entry, or confirmation should be paired through GNOME Bluetooth Settings.

### Hotspot

- Power toggle in the header
- Wi-Fi disconnection confirmation before starting
- Network name and revealable password
- Connected-client list based on the hotspot interface neighbor table
- Edit name/password subwindow
- Non-blocking start, stop, and save operations
- GNOME Network Settings shortcut

The first activation creates a persistent NetworkManager profile named `Moss Hotspot`. Later edits reuse that profile.

### Sound

- Header toggle mutes or unmutes the default output
- Output and microphone volume sliders, up to 150%
- Separate output and microphone mute buttons
- Current output and input device
- Device selection subwindow
- GNOME Sound Settings shortcut

Unlike Wi-Fi, Bluetooth, and hotspot, muting output does not hide the sound body because microphone controls must remain accessible.

## Arch Linux dependencies

```bash
sudo pacman -S --needed \
    python-gobject gtk4 libadwaita \
    networkmanager libnotify gnome-control-center \
    bluez bluez-utils \
    pipewire wireplumber \
    iproute2
```

Most Hyprland PipeWire installations also use:

```bash
sudo pacman -S --needed pipewire-audio pipewire-pulse
```

Enable the system services:

```bash
sudo systemctl enable --now NetworkManager.service
sudo systemctl enable --now bluetooth.service
```

PipeWire and WirePlumber normally run as user services or socket-activated services.

## Run from the project directory

```bash
chmod +x run-*.sh

./run-wifi.sh
./run-bluetooth.sh
./run-hotspot.sh
./run-sound.sh
```

## Install local launchers

```bash
chmod +x install-local.sh
./install-local.sh
```

This installs:

```text
~/.local/bin/moss-wifi
~/.local/bin/moss-bluetooth
~/.local/bin/moss-hotspot
~/.local/bin/moss-sound
```

## Waybar examples

```json
"network": {
    "format-wifi": "",
    "format-disconnected": "󰖪",
    "on-click": "moss-wifi",
    "on-click-right": "moss-hotspot"
},

"bluetooth": {
    "format": "",
    "format-disabled": "󰂲",
    "format-connected": "󰂱",
    "on-click": "moss-bluetooth"
},

"pulseaudio": {
    "format": "{icon}",
    "format-muted": "󰝟",
    "format-icons": ["󰕿", "󰖀", "󰕾"],
    "on-click": "moss-sound"
}
```

## Hyprland window rules

```ini
windowrulev2 = float, class:^(io.github.moss.ControlCenter.(Wifi|Bluetooth|Hotspot|Sound))$
windowrulev2 = center, class:^(io.github.moss.ControlCenter.(Wifi|Bluetooth|Hotspot|Sound))$
windowrulev2 = size 400 560, class:^(io.github.moss.ControlCenter.(Wifi|Hotspot|Sound))$
windowrulev2 = size 400 600, class:^(io.github.moss.ControlCenter.Bluetooth)$
```

If your Hyprland version uses the newer rule syntax, translate the same class matches into that syntax.

## Project structure

```text
moss-control-center/
├── wifi.py
├── bluetooth.py
├── hotspot.py
├── sound.py
├── common/
│   ├── async_worker.py
│   ├── widgets.py
│   ├── window.py
│   └── style.css
├── services/
│   ├── network.py
│   ├── bluetooth.py
│   ├── hotspot.py
│   └── audio.py
├── run-wifi.sh
├── run-bluetooth.sh
├── run-hotspot.sh
├── run-sound.sh
└── install-local.sh
```

## Backend commands

- Wi-Fi and hotspot: NetworkManager through `nmcli`
- Bluetooth: BlueZ through `bluetoothctl`
- Sound: PipeWire/WirePlumber through `wpctl`
- Notifications: `notify-send`
- Full settings: `gnome-control-center`

All blocking backend commands run outside GTK's main thread.
