-- Disable auto-formatting for C files (prevents conform/formatters from changing tabs on save)
-- Also enforce 4-columns tabs locally for C buffers to satisfy norminette
vim.b.autoformat = false
vim.opt_local.tabstop = 4
vim.opt_local.shiftwidth = 4
vim.opt_local.softtabstop = 4
vim.opt_local.expandtab = false
