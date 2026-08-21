cd ~/.dotfiles

# First unstow, so existing symlinks are removed cleanly
stow -D -t "$HOME" home

# Move the new config directories into the repo
# type here mv command for the new configurations files
# For Example: mv ~/.config/control-center home/.config/

# Re-create all symlinks
stow -v -t "$HOME" home
