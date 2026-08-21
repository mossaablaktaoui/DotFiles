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

-- Look and Feel
hl.config({
	general = {
		gaps_in = 2,
		gaps_out = 5,
		border_size = 1,
		col = {
			active_border = { colors = { "rgba(33ccffee)", "rgba(00ff99ee)" }, angle = 45 },
			inactive_border = "rgba(595959aa)",
		},
		resize_on_border = true,
		allow_tearing = false,
		layout = "dwindle",
	},
	decoration = {
		rounding = 10,
		rounding_power = 2,
		active_opacity = 1.0,
		inactive_opacity = 0.8,
		shadow = {
			enabled = true,
			range = 4,
			render_power = 3,
			color = 0xee1a1a1a,
		},
		blur = {
			enabled = true,
			size = 5,
			passes = 10,
			vibrancy = 0.1696,
		},
	},
	animations = {
		enabled = true,
	},
	cursor = {
		no_warps = true,
		warp_on_change_workspace = 0,
		persistent_warps = false,
	},
})

-- Bezier curves
hl.curve("easeOutQuint", { type = "bezier", points = { { 0.23, 1 }, { 0.32, 1 } } })
hl.curve("easeInOutCubic", { type = "bezier", points = { { 0.65, 0.05 }, { 0.36, 1 } } })
hl.curve("linear", { type = "bezier", points = { { 0, 0 }, { 1, 1 } } })
hl.curve("almostLinear", { type = "bezier", points = { { 0.5, 0.5 }, { 0.75, 1 } } })
hl.curve("quick", { type = "bezier", points = { { 0.15, 0 }, { 0.1, 1 } } })
hl.curve("easeOutExpo", { type = "bezier", points = { { 0.16, 1 }, { 0.3, 1 } } })
hl.curve("easy", { type = "spring", mass = 1, stiffness = 71.2633, dampening = 15.8273644 })

-- Animations
hl.animation({ leaf = "global", enabled = true, speed = 10, bezier = "default" })
hl.animation({ leaf = "border", enabled = true, speed = 5.39, bezier = "easeOutQuint" })
hl.animation({ leaf = "windows", enabled = true, speed = 4.79, spring = "easy" })
hl.animation({ leaf = "windowsIn", enabled = true, speed = 4.1, spring = "easy", style = "popin 87%" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 1.49, bezier = "linear", style = "popin 87%" })
hl.animation({ leaf = "fadeIn", enabled = true, speed = 1.73, bezier = "almostLinear" })
hl.animation({ leaf = "fadeOut", enabled = true, speed = 1.46, bezier = "almostLinear" })
hl.animation({ leaf = "fade", enabled = true, speed = 3.03, bezier = "quick" })
hl.animation({ leaf = "layers", enabled = true, speed = 3.81, bezier = "easeOutQuint" })
hl.animation({ leaf = "layersIn", enabled = true, speed = 4, bezier = "easeOutQuint", style = "fade" })
hl.animation({ leaf = "layersOut", enabled = true, speed = 1.5, bezier = "linear", style = "fade" })
hl.animation({ leaf = "fadeLayersIn", enabled = true, speed = 1.79, bezier = "almostLinear" })
hl.animation({ leaf = "fadeLayersOut", enabled = true, speed = 1.39, bezier = "almostLinear" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 7, bezier = "easeOutQuint", style = "slide" })
hl.animation({ leaf = "workspacesIn", enabled = true, speed = 7, bezier = "easeOutQuint", style = "slide" })
hl.animation({ leaf = "workspacesOut", enabled = true, speed = 7, bezier = "easeOutQuint", style = "slide" })
hl.animation({ leaf = "zoomFactor", enabled = true, speed = 7, bezier = "quick" })

-- Layouts
hl.config({
	dwindle = {
		preserve_split = false,
	},
	master = {
		new_status = "master",
	},
})

-- Misc
hl.config({
	misc = {
		force_default_wallpaper = 1,
		disable_hyprland_logo = false,
	},
})

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
hl.env("XDG_CURRENT_DESKTOP", "Hyprland")
hl.env("XDG_SESSION_DESKTOP", "Hyprland")
hl.env("XDG_SESSION_TYPE", "wayland")

hl.on("hyprland.start", function()
	local variables = "WAYLAND_DISPLAY XDG_CURRENT_DESKTOP XDG_SESSION_DESKTOP XDG_SESSION_TYPE"

	hl.exec_cmd("dbus-update-activation-environment --systemd " .. variables)
	hl.exec_cmd("systemctl --user import-environment " .. variables)
end)

hl.permission("/usr/(lib|libexec|lib64)/xdg-desktop-portal-hyprland", "screencopy", "allow")
