# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
project = 'Personal Notes'
copyright = '2026, elio'
author = 'elio'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'zh_CN'

# -- Options for HTML output -------------------------------------------------
html_theme = 'shibuya'
html_static_path = ['_static']

# Shibuya 主题配置
html_theme_options = {
    'accent_color': 'blue',
    'github_repo': 'yezong7/note',
    'globaltoc_expand_depth': 2,
}

# MyST-Parser 支持 Markdown
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

myst_enable_extensions = [
    'colon_fence',
    'deflist',
]
