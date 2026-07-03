-- Make Neovim background transparent and keep it transparent across colorscheme changes
-- Place this file at: lua/config/transparent.lua

local M = {}

-- Enable true color support
vim.opt.termguicolors = true

local function set_transparent()
  local hl = vim.api.nvim_set_hl
  -- Set main background to none
  pcall(hl, 0, "Normal", { bg = "none" })
  pcall(hl, 0, "NormalFloat", { bg = "none" })
  pcall(hl, 0, "NormalNC", { bg = "none" })
  pcall(hl, 0, "SignColumn", { bg = "none" })
  pcall(hl, 0, "TelescopeNormal", { bg = "none" })
  pcall(hl, 0, "EndOfBuffer", { fg = "none" })

  -- Some plugins use these
  pcall(hl, 0, "NvimTreeNormal", { bg = "none" })
  pcall(hl, 0, "NvimTreeNormalNC", { bg = "none" })
  pcall(hl, 0, "FloatBorder", { bg = "none" })
  pcall(hl, 0, "NormalFloat", { bg = "none" })
end

-- Apply on startup
set_transparent()

-- Re-apply after every colorscheme change
vim.api.nvim_create_autocmd("ColorScheme", {
  pattern = "*",
  callback = function()
    set_transparent()
  end,
})

return M
