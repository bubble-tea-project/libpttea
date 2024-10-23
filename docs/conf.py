# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'LibPttea'
copyright = '2024, vHrqO'
author = 'vHrqO'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',
              'myst_parser',
              ]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'

html_title = "LibPttea"

html_favicon = "_static/bubble_tea_flat.svg"


# A list of paths that contain custom static files (such as style sheets or script files). 
# Relative paths are taken as relative to the configuration directory. 
# They are copied to the output’s _static directory after the theme’s static files,
#  so a file named default.css will overwrite the theme’s default.css.
html_static_path = ['_static']
