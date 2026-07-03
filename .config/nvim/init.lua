-- Set mapping timeout to 150 milliseconds
vim.opt.timeoutlen = 150

-- Set key code timeout (for escape sequences/arrows) to 50 milliseconds
vim.opt.ttimeoutlen = 50
-- bootstrap lazy.nvim, LazyVim and your plugins
require("config.lazy")

-- Make Neovim background transparent (loads after colorscheme/plugins)
pcall(require, "config.transparent")
