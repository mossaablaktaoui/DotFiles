return {
  -- Disable Flash.nvim (LazyVim default jump/search plugin)
  { "folke/flash.nvim", enabled = false },

  -- Disable builtin LSP inlay hints globally
  {
    "neovim/nvim-lspconfig",
    opts = {
      inlay_hints = {
        enabled = false,
      },
    },
  },
}
