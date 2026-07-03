return {
  -- Extra themes only. The LazyVim default theme stays unchanged.
  { "srcery-colors/srcery-vim" },
  {
    "catppuccin/nvim",
    name = "catppuccin",
  },
  { "ellisonleao/gruvbox.nvim" },
  { "bluz71/vim-moonfly-colors" },
  { "tpope/vim-vividchalk" },
  { "jacoborus/tender.vim" },

  {
    "zaldih/themery.nvim",
    cmd = "Themery",
    opts = {
      themes = {
        "tokyonight",
        "srcery",
        "catppuccin",
        "gruvbox",
        "moonfly",
        "vividchalk",
        "tender",
      },
      livePreview = true,
    },
  },
}
