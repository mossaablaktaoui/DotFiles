-- Programs
local filemanager = "spf"
local launcher = "rofi -show drun"
local terminal = "kitty"

local ALT = "ALT"
local SUPER = "SUPER"

-- Applications
hl.bind(SUPER .. " + T", hl.dsp.exec_cmd(terminal))
-- hl.bind(ALT .. " + F", hl.dsp.exec_cmd(filemanager))

-- Windows
hl.bind(SUPER .. " + E", hl.dsp.window.close())
hl.bind(SUPER .. " + V", hl.dsp.window.float({ action = "toggle" }))
hl.bind(SUPER .. " + F", hl.dsp.window.fullscreen())

-- Focus
hl.bind(ALT .. " + H", hl.dsp.focus({ direction = "left" }))
hl.bind(ALT .. " + J", hl.dsp.focus({ direction = "down" }))
hl.bind(ALT .. " + K", hl.dsp.focus({ direction = "up" }))
hl.bind(ALT .. " + L", hl.dsp.focus({ direction = "right" }))

-- Language switch
hl.bind("SUPER + SPACE", hl.dsp.exec_cmd("hyprctl switchxkblayout all next"))

-- wallpaper switch
hl.bind("SUPER + S", hl.dsp.exec_cmd("waypaper --random"))

-- Resize
local function resize(x, y)
	return function()
		hl.dispatch(hl.dsp.window.resize({
			x = x,
			y = y,
			relative = true,
		}))
	end
end

hl.bind(ALT .. " + SHIFT + H", resize(-5, 0), { repeating = true })
hl.bind(ALT .. " + SHIFT + L", resize(5, 0), { repeating = true })
hl.bind(ALT .. " + SHIFT + K", resize(0, -5), { repeating = true })
hl.bind(ALT .. " + SHIFT + J", resize(0, 5), { repeating = true })

-- Swap windows
hl.bind(ALT .. " + CTRL + H", hl.dsp.window.swap({ direction = "l" }))
hl.bind(ALT .. " + CTRL + J", hl.dsp.window.swap({ direction = "d" }))
hl.bind(ALT .. " + CTRL + K", hl.dsp.window.swap({ direction = "u" }))
hl.bind(ALT .. " + CTRL + L", hl.dsp.window.swap({ direction = "r" }))

-- Workspaces
for i = 1, 10 do
	local key = i == 10 and "0" or tostring(i)

	hl.bind(SUPER .. " + " .. key, hl.dsp.focus({ workspace = i }))

	hl.bind(
		SUPER .. " + SHIFT + " .. key,
		hl.dsp.window.move({
			workspace = i,
			follow = false, -- movetoworkspacesilent
		})
	)
end

-- Relative Workspace navigation
hl.bind(SUPER .. " + H", function()
	hl.dispatch(hl.dsp.focus({ workspace = "-1" }))
end)
hl.bind(SUPER .. " + L", function()
	hl.dispatch(hl.dsp.focus({ workspace = "+1" }))
end)

-- Move window to previous/next workspace
hl.bind(SUPER .. " + SHIFT + H", function()
	hl.dispatch(hl.dsp.window.move({
		workspace = "-1",
		follow = false,
	}))
	hl.dispatch(hl.dsp.focus({ workspace = "-1" }))
end)

hl.bind(SUPER .. " + SHIFT + L", function()
	hl.dispatch(hl.dsp.window.move({
		workspace = "+1",
		follow = false,
	}))
	hl.dispatch(hl.dsp.focus({ workspace = "+1" }))
end)

-- Session
hl.bind(SUPER .. " + M", hl.dsp.exit())
hl.bind(
	SUPER .. " + SHIFT + R",
	hl.dsp.exec_cmd(
		'hyprctl reload; pkill swaync; swaync; pkill waybar; waybar; sleep 1 && notify-send "Hyprland" "Configuration reloaded sucessfully"'
	)
)
hl.bind(SUPER .. " + CTRL + L", hl.dsp.exec_cmd("hyprlock"))

-- Mouse scrolling emulation
hl.bind(SUPER .. " + J", function()
	hl.exec_cmd("/usr/bin/ydotool mousemove --wheel -- 0 -1")
end, { repeating = true })

hl.bind(SUPER .. " + K", function()
	hl.exec_cmd("/usr/bin/ydotool mousemove --wheel -- 0 1")
end, { repeating = true })

-- Screenshots
hl.bind("Print", hl.dsp.exec_cmd("~/.config/hypr/scripts/screenshot.sh area"))
hl.bind("SHIFT + Print", hl.dsp.exec_cmd("~/.config/hypr/scripts/screenshot.sh screen"))
hl.bind(SUPER .. " + SHIFT + S", hl.dsp.exec_cmd("~/.config/hypr/scripts/screenshot.sh area"))

-- rofi
hl.bind(SUPER .. " + A", hl.dsp.exec_cmd("pkill rofi || rofi -show drun -config ~/.config/rofi/launcher.rasi"))
hl.bind(ALT .. " + F", hl.dsp.exec_cmd("pkill rofi || rofi -show filebrowser -config ~/.config/rofi/launcher.rasi"))
hl.bind(SUPER .. " + R", hl.dsp.exec_cmd("pkill rofi || rofi -show run -config ~/.config/rofi/launcher.rasi"))
hl.bind(SUPER .. " + W", hl.dsp.exec_cmd("pkill rofi || rofi -show window -config ~/.config/rofi/launcher.rasi"))
hl.bind(SUPER .. " + C", hl.dsp.exec_cmd("pkill rofi || ~/.config/rofi/scripts/clipboard-menu"))

-- swaync
hl.bind(SUPER .. " + N", hl.dsp.exec_cmd("swaync-client -t"))

-- Power menu
hl.bind(SUPER .. " + P", hl.dsp.exec_cmd("pkill rofi || ~/.config/rofi/scripts/power-menu"))

-- Laptop multimedia keys
hl.bind(
	"XF86AudioRaiseVolume",
	hl.dsp.exec_cmd("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+"),
	{ locked = true, repeating = true }
)
hl.bind(
	"XF86AudioLowerVolume",
	hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"),
	{ locked = true, repeating = true }
)
hl.bind(
	"XF86AudioMute",
	hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"),
	{ locked = true, repeating = true }
)
hl.bind(
	"XF86AudioMicMute",
	hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"),
	{ locked = true, repeating = true }
)
hl.bind("XF86MonBrightnessUp", hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%+"), { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%-"), { locked = true, repeating = true })

hl.bind("XF86AudioNext", hl.dsp.exec_cmd("playerctl next"), { locked = true })
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPlay", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPrev", hl.dsp.exec_cmd("playerctl previous"), { locked = true })

-- run qt design studio
hl.bind(SUPER .. " + Q", hl.dsp.exec_cmd("QT_QPA_PLATFORM=xcb ~/Qt/Tools/QtDesignStudio/bin/qtdesignstudio"))
