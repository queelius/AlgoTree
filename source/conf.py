# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("../.."))


project = "AlgoTree"
copyright = "2024, Alex Towell"
author = "Alex Towell"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx'
]

# Suppress ipython3 lexer warnings
suppress_warnings = ['misc.highlighting_failure']

# Add support for ipython3 code blocks
pygments_style = 'sphinx'

templates_path = ['_templates']
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = 'alabaster'
#html_theme = 'sphinx_rtd_theme'
#html_theme = 'classic'


# Only add paths that exist
html_static_path = []
if os.path.exists('_static'):
    html_static_path.append('_static')
if os.path.exists('images'):
    html_static_path.append('images')

