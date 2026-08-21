-- Monitor
hl.monitor({
	output = "eDP-1",
	mode = "1600x900@60",
	position = "0x0",
	scale = "1",
})

-- Autostart
hl.on("hyprland.start", function()
	hl.exec_cmd("awww-daemon")
	hl.exec_cmd("waybar")
	hl.exec_cmd("swaync")
	hl.exec_cmd("while true; do waypaper --random; sleep 300; done")
end)

-- Environment variables
hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")
hl.env("XCURSOR_THEME", "Adwaita")
hl.env("GTK_THEME", "Adwaita:dark")
-- hl.env("QT_QPA_PLATFORMTHEME", "qt5ct")
hl.env("XDG_CURRENT_DESKTOP", "Hyprland")
hl.env("XDG_SESSION_DESKTOP", "Hyprland")
hl.env("XDG_SESSION_TYPE", "wayland")

-- Export environment to systemd/dbus
hl.on("hyprland.start", function()
	local variables = "WAYLAND_DISPLAY XDG_CURRENT_DESKTOP XDG_SESSION_DESKTOP XDG_SESSION_TYPE"

	hl.exec_cmd("dbus-update-activation-environment --systemd " .. variables)
	hl.exec_cmd("systemctl --user import-environment " .. variables)
end)

-- Input
hl.config({
	input = {
		kb_layout = "us,ara",
		kb_variant = "",
		kb_model = "",
		kb_options = "grp:alt_space_toggle",
		kb_rules = "",
		repeat_rate = 35,
		repeat_delay = 300,
		follow_mouse = 1,
		sensitivity = 0,
		touchpad = {
			natural_scroll = false,
		},
	},
})

-- Window rules
hl.window_rule({
	name = "suppress-maximize-events",
	match = { class = ".*" },
	suppress_event = "maximize",
})

hl.window_rule({
	name = "fix-xwayland-drags",
	match = {
		class = "^$",
		title = "^$",
		xwayland = true,
		float = true,
		fullscreen = false,
		pin = false,
	},
	no_focus = true,
})

-- Float certain dialogs
for _, cls in ipairs({ "pavucontrol", "blueman-manager", "qt5ct", "org.kde.polkit-kde-authentication-agent-1" }) do
	hl.window_rule({
		match = { class = cls },
		float = true,
	})
end

hl.window_rule({
	name = "firefox-pip",
	match = { class = "firefox", title = "Picture-in-Picture" },
	float = true,
	pin = true,
})

hl.window_rule({
	name = "imv-image-viewer",
	match = { class = "imv" },
	float = true,
})

hl.window_rule({
	match = { class = "mpv" },
	float = true,
})

hl.window_rule({
	name = "bluetooth-control-center",
	match = { class = "io.github.moss.ControlCenter.Bluetooth" },
	border_size = 0,
})

-- Permissions
hl.permission("/usr/(lib|libexec|lib64)/xdg-desktop-portal-hyprland", "screencopy", "allow")
