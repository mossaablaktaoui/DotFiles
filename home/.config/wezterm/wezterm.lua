local wezterm = require("wezterm")
local act = wezterm.action
local config = wezterm.config_builder()

-- General

-- config.color_scheme = 'Modus-Vivendi-Tinted'
-- config.color_scheme = 'Modus-Vivendi-Tritanopia'
-- config.color_scheme = 'Molokai (Gogh)'
config.color_scheme = "Spacedust"

-- config.font_size = 13

-- Appearance
config.window_decorations = "RESIZE"
config.hide_tab_bar_if_only_one_tab = true

config.window_padding = {
	left = 0,
	right = 0,
	top = 0,
	bottom = 0,
}

config.color_scheme = "Tokyo Night"
config.font_size = 13

-- Appearance - background opacity
config.window_background_opacity = 0.85

-- Shortcuts

local keys = {
	-- Tabs
	{
		key = "t",
		mods = "CTRL|SHIFT",
		action = act.SpawnTab("CurrentPaneDomain"),
	},
	{
		key = "w",
		mods = "CTRL|SHIFT",
		action = act.CloseCurrentTab({ confirm = true }),
	},
	{
		key = "Tab",
		mods = "CTRL",
		action = act.ActivateTabRelative(1),
	},
	{
		key = "Tab",
		mods = "CTRL|SHIFT",
		action = act.ActivateTabRelative(-1),
	},

	-- Splits
	{
		key = "\\",
		mods = "ALT",
		action = act.SplitHorizontal({ domain = "CurrentPaneDomain" }),
	},
	{
		key = "/",
		mods = "ALT",
		action = act.SplitVertical({ domain = "CurrentPaneDomain" }),
	},

	-- Close pane
	{
		key = "e",
		mods = "ALT",
		action = act.CloseCurrentPane({ confirm = true }),
	},

	-- Move between WezTerm panes
	{
		key = "h",
		mods = "ALT",
		action = act.ActivatePaneDirection("Left"),
	},
	{
		key = "j",
		mods = "ALT",
		action = act.ActivatePaneDirection("Down"),
	},
	{
		key = "k",
		mods = "ALT",
		action = act.ActivatePaneDirection("Up"),
	},
	{
		key = "l",
		mods = "ALT",
		action = act.ActivatePaneDirection("Right"),
	},
	{
		key = "w",
		mods = "ALT",
		action = act.ActivatePaneDirection("Next"),
	},

	-- Resize panes
	{
		key = "H",
		mods = "ALT|SHIFT",
		action = act.AdjustPaneSize({ "Left", 1 }),
	},
	{
		key = "J",
		mods = "ALT|SHIFT",
		action = act.AdjustPaneSize({ "Down", 1 }),
	},
	{
		key = "K",
		mods = "ALT|SHIFT",
		action = act.AdjustPaneSize({ "Up", 1 }),
	},
	{
		key = "L",
		mods = "ALT|SHIFT",
		action = act.AdjustPaneSize({ "Right", 1 }),
	},

	-- Clipboard
	{
		key = "p",
		mods = "ALT",
		action = act.PasteFrom("Clipboard"),
	},
	{
		key = "y",
		mods = "ALT",
		action = act.CopyTo("Clipboard"),
	},

	-- Scroll terminal (Ctrl+Shift + j/k)
	{
		key = "j",
		mods = "CTRL|SHIFT",
		action = act.ScrollByLine(1),
	},
	{
		key = "k",
		mods = "CTRL|SHIFT",
		action = act.ScrollByLine(-1),
	},

	-- Zoom pane
	{
		key = "f",
		mods = "ALT",
		action = act.TogglePaneZoomState,
	},

	-- Swap panes with Alt+Ctrl+hjkl removed because unsupported

	-- Rotate panes clockwise
	{
		key = "r",
		mods = "ALT",
		action = act.RotatePanes("Clockwise"),
	},

	-- On-demand 3-pane layout (Ctrl+Alt+n) — splits the current window's active pane
	{
		key = "n",
		mods = "CTRL|ALT",
		action = wezterm.action_callback(function(win, pane)
			-- Use the current window/pane instead of spawning a new window
			local tab = win:active_tab()
			local p = tab:active_pane()
			local right = p:split({ direction = "Right", size = 0.5 })
			right:split({ direction = "Down", size = 0.5 })
		end),
	},

	-- Activate Copy Mode
	{
		key = "c",
		mods = "ALT",
		action = wezterm.action.ActivateCopyMode,
	},
}

-- Note: removed the gui-startup automatic spawn to avoid creating an extra window
-- and potential startup errors. Use the shortcut (Ctrl+Alt+n) to create the 3-pane layout
-- inside the current window on demand.

-- Dynamic indicator for COPY and VISUAL modes
wezterm.on("update-status", function(window, pane)
	local name = window:active_key_table()

	if name == "copy_mode" then
		if pane:get_has_selection() then
			window:set_right_status(wezterm.format({
				{ Background = { Color = "#ff55ff" } },
				{ Foreground = { Color = "#ffffff" } },
				{ Attribute = { Intensity = "Bold" } },
				{ Text = "  VIM VISUAL MODE  " },
			}))
		else
			window:set_right_status(wezterm.format({
				{ Background = { Color = "#50fa7b" } },
				{ Foreground = { Color = "#282a36" } },
				{ Attribute = { Intensity = "Bold" } },
				{ Text = "  VIM COPY MODE  " },
			}))
		end
	else
		window:set_right_status("")
	end
end)

config.keys = keys

return config
