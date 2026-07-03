-- Keymaps are automatically loaded on the VeryLazy event
-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua
-- Add any additional keymaps here

vim.keymap.set("n", "<leader>o", "o<Esc>", { desc = "New Line Below" })
vim.keymap.set("n", "<leader>O", "O<Esc>", { desc = "New Line Above" })

vim.keymap.set("n", "<leader>bn", "<cmd>bnext<CR>", { desc = "Next Buffer" })
vim.keymap.set("n", "<leader>bp", "<cmd>bprevious<CR>", { desc = "Previous Buffer" })

vim.keymap.set("i", "jj", "<Esc>", { desc = "Escape" })

vim.keymap.set("t", "jj", [[<C-\><C-n>]], { desc = "Exit Terminal Mode" })


-- Save / quit shortcuts.
vim.keymap.set("n", "<leader>C", "<cmd>wa<CR><cmd>qall<CR>", { desc = "Save All and Quit Neovim" })
vim.keymap.set("n", "<leader>W", "<cmd>wa<CR>", { desc = "Save All Buffers" })
