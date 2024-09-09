# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Illuminator'
copyright = '2024, Illuminator Team'
author = 'Illuminator Team'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["myst_parser",
              'sphinx_rtd_theme',
              'sphinx.ext.autodoc',
              'sphinx.ext.napoleon',
              'sphinx_copybutton',
              ]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = [
    'css/custom.css',
]
html_logo = "_static/img/illuminator.jpg"
html_theme_options = {
    'logo_only': True,
    'display_version': False,
    'collapse_navigation': True,
}

