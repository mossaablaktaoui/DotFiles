return {
  -- Mason is already used by LazyVim. This only asks it to install your Python tools.
  {
    "mason-org/mason.nvim",
    opts = {
      ensure_installed = {
        "basedpyright",
        "ruff",
        "flake8",
        "mypy",
        "clangd",
      },
    },
  },

  -- LazyVim already uses nvim-lspconfig. This enables your Python language servers.
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        basedpyright = {},
        ruff = {},
        clangd = {},
      },
    },
  },

  -- LazyVim already uses conform.nvim. This formats Python with ruff on save.
  {
    "stevearc/conform.nvim",
    opts = {
      formatters_by_ft = {
        python = { "ruff_format" },
      },
    },
  },

  -- External linting with flake8 and mypy.
  {
    "mfussenegger/nvim-lint",
    event = { "BufReadPre", "BufNewFile" },
    config = function()
      local lint = require("lint")

      lint.linters_by_ft = {
        python = { "flake8", "mypy" },
      }

      vim.api.nvim_create_autocmd({ "BufWritePost", "BufReadPost", "InsertLeave" }, {
        callback = function()
          lint.try_lint()
        end,
      })
    end,
  },
}
