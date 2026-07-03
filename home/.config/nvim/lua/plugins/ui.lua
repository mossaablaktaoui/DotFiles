return {
  {
    "mg979/vim-visual-multi",
    branch = "master",
  },

  {
    "sphamba/smear-cursor.nvim",
    event = "VeryLazy",
    opts = {
      enabled = true,
      smear_between_buffers = true,
      stiffness = 0.5,
      trailing_stiffness = 0.5,
      distance_stop_animating = 0.2,
    },
  },

  -- Same Comment.nvim setup as your old dotfiles.
  {
    "numToStr/Comment.nvim",
    opts = {},
  },

  {
    "Mirsmog/real-icons.nvim",
    build = ":RealIconsInstallPack material",
    opts = {
      pack = "material",
      integrations = {
        snacks_picker = true,
      },
    },
  },
}
