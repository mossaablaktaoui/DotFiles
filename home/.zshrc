# Zsh configuration

# - Oh My Zsh
# - PATH / local apps
# - aliases
# - NVM
# - Vi mode
# - Yazi helper

# ============================================================
# Oh My Zsh
# ============================================================

export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="robbyrussell"

# Keep plugins minimal for faster startup

plugins=(git)

source "$ZSH/oh-my-zsh.sh"

# ============================================================
# PATH
# ============================================================

# Keep all custom binaries here so they are available everywhere.

export PATH="$HOME/.local/bin:$PATH"
export PATH="$HOME/.npm-global/bin:$PATH"
export PATH="$HOME/.opencode/bin:$PATH"

# ============================================================
# Default programs
# ============================================================

# Use your local Neovim AppImage as the main editor

export EDITOR="$HOME/.apps/neovim/nvim-linux-x86_64.appimage"
export VISUAL="$HOME/.apps/neovim/nvim-linux-x86_64.appimage"

# ============================================================
# NVM / Node.js
# ============================================================

export NVM_DIR="$HOME/.nvm"

if [ -s "$NVM_DIR/nvm.sh" ]; then
. "$NVM_DIR/nvm.sh"
nvm use --silent default
fi

if [ -s "$NVM_DIR/bash_completion" ]; then
. "$NVM_DIR/bash_completion"
fi

# ============================================================
# Aliases — general
# ============================================================

alias c="clear"
alias e="exit"
alias s="source ~/.zshrc"
alias p="python3"
alias n="norminette"

# App shortcuts
alias nvim="$HOME/.apps/neovim/nvim-linux-x86_64.appimage"
alias wezterm="$HOME/.apps/wezterm/AppRun"

# ============================================================
# Aliases — system / GNOME
# ============================================================

alias enbaledhikr="systemctl --user enable dhikr-reminder.timer"

# Swap Alt and Win keys in GNOME
alias swap_alt_win="gsettings set org.gnome.desktop.input-sources xkb-options \"['altwin:swap_alt_win']\""
alias unswap_alt_win="gsettings set org.gnome.desktop.input-sources xkb-options \"[]\""

# ============================================================
# Zsh Vi mode
# ============================================================

# Use Vim-style command mode in the shell
bindkey -v

# Faster escape from insert mode
bindkey -M viins 'jj' vi-cmd-mode

# Lower delay for key sequences
export KEYTIMEOUT=20

# Right prompt indicators
VIM_INS_MODE="%F{cyan}[INSERT]%f"
VIM_CMD_MODE="%F{green}[NORMAL]%f"

# Update prompt + cursor shape when switching modes
function zle-keymap-select {
if [[ $KEYMAP == vicmd ]]; then
RPROMPT=$VIM_CMD_MODE
echo -ne "\e[2 q"   # block cursor
else
RPROMPT=$VIM_INS_MODE
echo -ne "\e[6 q"   # beam cursor
fi
zle reset-prompt
}
zle -N zle-keymap-select

# Start each prompt in insert mode
function zle-line-init {
RPROMPT=$VIM_INS_MODE
echo -ne "\e[6 q"
zle reset-prompt
}
zle -N zle-line-init

# ============================================================
# Yazi helper
# ============================================================

# Open Yazi and automatically cd into the last directory when exiting.
function y() {
local tmp cwd
tmp="$(mktemp -t "yazi-cwd.XXXXXX")"

yazi "$@" --cwd-file="$tmp"

if cwd="$(command cat -- "$tmp")" && [ -n "$cwd" ] && [ "$cwd" != "$PWD" ]; then
builtin cd -- "$cwd"
fi

rm -f -- "$tmp"
}
