-- Options are automatically loaded before lazy.nvim startup
-- Default options that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/options.lua
-- Add any additional options here

-- Show absolute line numbers.
vim.opt.number = true

-- Display a tab as 4 columns, but keep actual tab characters.
-- tabstop: width of a TAB character (how it is displayed)
-- shiftwidth: width used for autoindent and >> << operations
-- softtabstop: number of spaces a <Tab> counts for while editing (pressing Tab)
-- expandtab = false ensures real TAB characters are inserted, not spaces.
vim.opt.tabstop = 4
vim.opt.shiftwidth = 4
vim.opt.softtabstop = 4
vim.opt.expandtab = false

-- Make Tab key behave naturally when inserting (useful with softtabstop)
vim.opt.smarttab = true

-- Automatically indent new lines based on the current code context.
vim.opt.smartindent = true

-- Search without caring about uppercase or lowercase letters.
vim.opt.ignorecase = true

-- Keep search results highlighted.
vim.opt.hlsearch = true

-- Enable true color support for better themes.
vim.opt.termguicolors = true

-- Highlight the line where the cursor is.
vim.opt.cursorline = true

-- Do not visually wrap long lines.
vim.opt.wrap = false

-- Use the system clipboard with Neovim.
vim.opt.clipboard = "unnamedplus"

-- Save undo history even after closing Neovim.
vim.opt.undofile = true

-- Enable relative numbers.
vim.opt.relativenumber = true

-- Keep at least 20 lines above/below the cursor.
vim.opt.scrolloff = 20
