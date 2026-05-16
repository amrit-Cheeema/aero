# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
import plotly

sys.path.insert(0, os.path.abspath('..')) 
sys.path.insert(0, os.path.abspath(os.path.dirname(plotly.__file__)))

project = 'aero'
copyright = '2026, Amrit Cheema'
author = 'Amrit Cheema'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',  # This fixes the "Unknown directive" error
    'sphinx.ext.napoleon', # This allows Google/NumPy style docstrings
    'sphinx.ext.mathjax',  # This renders your physics equations
    
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
