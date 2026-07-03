# If you come from bash you might have to change your $PATH.
# export PATH=$HOME/bin:$HOME/.local/bin:/usr/local/bin:$PATH

# Path to your Oh My Zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time Oh My Zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/ohmyzsh/ohmyzsh/wiki/Themes
ZSH_THEME="robbyrussell"

# Set list of themes to pick from when loading at random
# Setting this variable when ZSH_THEME=random will cause zsh to load
# a theme from this variable instead of looking in $ZSH/themes/
# If set to an empty array, this variable will have no effect.
# ZSH_THEME_RANDOM_CANDIDATES=( "robbyrussell" "agnoster" )

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion.
# Case-sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Uncomment one of the following lines to change the auto-update behavior
# zstyle ':omz:update' mode disabled  # disable automatic updates
# zstyle ':omz:update' mode auto      # update automatically without asking
# zstyle ':omz:update' mode reminder  # just remind me to update when it's time

# Uncomment the following line to change how often to auto-update (in days).
# zstyle ':omz:update' frequency 13

# Uncomment the following line if pasting URLs and other text is messed up.
# DISABLE_MAGIC_FUNCTIONS="true"

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# You can also set it to another string to have that shown instead of the default red dots.
# e.g. COMPLETION_WAITING_DOTS="%F{yellow}waiting...%f"
# Caution: this setting can cause issues with multiline prompts in zsh < 5.7.1 (see #5765)
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# You can set one of the optional three formats:
# "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# or set a custom format using the strftime function format specifications,
# see 'man strftime' for details.
# HIST_STAMPS="mm/dd/yyyy"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# Which plugins would you like to load?
# Standard plugins can be found in $ZSH/plugins/
# Custom plugins may be added to $ZSH_CUSTOM/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(git)

source $ZSH/oh-my-zsh.sh

# User configuration

# export MANPATH="/usr/local/man:$MANPATH"

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

# Preferred editor for local and remote sessions
# if [[ -n $SSH_CONNECTION ]]; then
#   export EDITOR='vim'
# else
#   export EDITOR='nvim'
# fi

# Compilation flags
# export ARCHFLAGS="-arch $(uname -m)"

# Set personal aliases, overriding those provided by Oh My Zsh libs,
# plugins, and themes. Aliases can be placed here, though Oh My Zsh
# users are encouraged to define aliases within a top-level file in
# the $ZSH_CUSTOM folder, with .zsh extension. Examples:
# - $ZSH_CUSTOM/aliases.zsh
# - $ZSH_CUSTOM/macos.zsh
# For a full list of active aliases, run `alias`.
#
# Example aliases
# alias zshconfig="mate ~/.zshrc"
# alias ohmyzsh="mate ~/.oh-my-zsh"
#
#

#if [ -z "$TMUX" ]; then
#	    tmux
#fi



alias git_all="git add .; git commit -m 'push'; git push; git ls-files"
alias p="python3"
alias c="clear"
alias v="nvim"
alias call="cd ~/goinfre/Call-Me-Maybe"
alias newalias="vim ~/.zshrc"
alias s="source ~/.zshrc"
alias e="exit"
alias moulinettetestset="cd ~/Call-Me-Maybe/ && uv run -m src --functions_definition moulinette/data/input/functions_definition.json --input moulinette/data/input/function_calling_tests.json"
alias moulinettetestrun="cd ~/Call-Me-Maybe/moulinette/ && uv run python -m moulinette grade_student_answers --set private --student_answer_path ../data/output/function_calling_results.json"
alias ask="gemini -p"
alias gem="gemini"
alias wezterm="$HOME/.apps/wezterm/AppRun"
alias configwez="nvim ~/.config/wezterm/wezterm.lua"
alias enbaledhikr="systemctl --user enable dhikr-reminder.timer"
alias gccp="gcc -g -pthread"
# Swap Alt and Win
alias swap_alt_win="gsettings set org.gnome.desktop.input-sources xkb-options \"['altwin:swap_alt_win']\""
alias unswap_alt_win="gsettings set org.gnome.desktop.input-sources xkb-options \"['altwin:disabled']\""


alias nvim="$HOME/.apps/neovim/nvim-linux-x86_64.appimage"
export PATH="$HOME/.local/bin:$PATH"

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/nvm.sh" ] && nvm use --silent default
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# npm global binaries
export PATH="$HOME/.npm-global/bin:$PATH"


# Added by Antigravity CLI installer
export PATH="/home/mlaktaou/.local/bin:$PATH"

# opencode
export PATH=/home/mlaktaou/.opencode/bin:$PATH


# Enable Vi mode and eliminate the switching delay
bindkey -v
bindkey -M viins 'jj' vi-cmd-mode
bindkey -M vicmd 'jj' vi-cmd-mode
export KEYTIMEOUT=20

# Define text indicators
VIM_INS_MODE="%F{cyan}[INSERT]%f"
VIM_CMD_MODE="%F{green}[NORMAL]%f"

# Automatically update prompt and cursor shape when mode changes
function zle-keymap-select {
  if [[ ${KEYMAP} == vicmd ]]; then
    RPROMPT=$VIM_CMD_MODE
    echo -ne "\e[2 q" # Solid Block for Normal Mode
  else
    RPROMPT=$VIM_INS_MODE
    echo -ne "\e[6 q" # Vertical Beam for Insert Mode
  fi
  zle reset-prompt
}
zle -N zle-keymap-select

# Reset to Insert mode for new lines
function zle-line-init {
  RPROMPT=$VIM_INS_MODE
  echo -ne "\e[6 q"
  zle reset-prompt
}
zle -N zle-line-init

export EDITOR=$HOME/.apps/neovim/nvim-linux-x86_64.appimage
export VISUAL=$HOME/.apps/neovim/nvim-linux-x86_64.appimage

# setup yazi
function y() {
	local tmp="$(mktemp -t "yazi-cwd.XXXXXX")" cwd
	yazi "$@" --cwd-file="$tmp"
	if cwd="$(command cat -- "$tmp")" && [ -n "$cwd" ] && [ "$cwd" != "$PWD" ]; then
		builtin cd -- "$cwd"
	fi
	rm -f -- "$tmp"
}
