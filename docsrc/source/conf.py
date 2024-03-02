# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath('../../fittrackee'))


# -- Project information -----------------------------------------------------

project = 'FitTrackee'
copyright = '2018 - 2024, SamR1'
author = 'SamR1'

# The full version, including alpha/beta/rc tags.
release = (Path(__file__).parent.parent.parent / 'VERSION').read_text()
# The short X.Y version.
version = release.split('-')[0]


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'recommonmark',
    'sphinxcontrib.httpdomain',
    'sphinxcontrib.autohttp.flask',
    'sphinx_copybutton',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_logo = "_static/ft-logo.png"

html_theme_options = {
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/SamR1/FitTrackee",
            "html": "",
            "class": "fa fa-github fa-lg",
        },
        {
            "name": "Mastodon",
            "url": "https://fosstodon.org/@FitTrackee",
            "html": "",
            "class": "fa fa-mastodon fa-lg",
        },
    ],
}

html_css_files = [
    'css/fork-awesome.min.css',
    'css/custom.css',
]

pygments_style = "sphinx"
pygments_dark_style = "monokai"

# -- Sources configuration ---------------------------------------------------

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}

# -- Internationalization ----------------------------------------------------

language = "en"
locale_dirs = ["../locales"]
gettext_compact = "docs"

languages = [
    ("English", "en"),  # English
    ("Français", "fr"),  # French
]
html_context = {"langs": languages}
