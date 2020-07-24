# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
# sys.path.insert(0, os.path.abspath('../..'))
# sys.path.insert(0, os.path.abspath('../../databay'))


# -- Project information -----------------------------------------------------

project = 'databay'
copyright = '2020, Voy Zan'
author = 'Voy Zan'

# The full version, including alpha/beta/rc tags
release = '0.1.0'

master_doc = 'index'
pygments_style = 'sphinx'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]

intersphinx_mapping = {
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
    'python': ('https://docs.python.org/3/', None),
    'apscheduler': ('https://apscheduler.readthedocs.io/en/stable/', None),
    'schedule': ('https://schedule.readthedocs.io/en/stable/', None),
}

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
import sphinx_rtd_theme

# html_theme = 'alabaster'
# html_theme = 'nature'
# html_theme = 'pyramid'
# html_theme = 'f5_sphinx_theme'
# html_theme = 'zerovm-sphinx-theme'


extensions.append("sphinx_rtd_theme")

html_theme = "sphinx_rtd_theme"

# html_sidebars = { '**': ['globaltoc.html', 'relations.html', 'sourcelink.html', 'searchbox.html'] }

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# autosummary_generate = True
# autoclass_content = 'both'

extensions.append('autoapi.extension')
autoapi_type = 'python'
autoapi_template_dir = '_autoapi_templates'
autoapi_root = 'api'
autoapi_dirs = [
    # '../../',
    # '../../databay',
    '../../databay',
]
# autoapi_ignore = [
#     # '*databay/__init__.py',
#     '*test*',
#     '*examples/*',
#     '*misc/*',
#     '*outlets/PrintOutlet.py',
#     '*outlets/CsvOutlet.py',
#     '*config.py',
#   ]
autoapi_options = [ 'members', 'undoc-members', 'xprivate-members', 'show-inheritance', 'show-module-summary', 'special-members', 'ximported-members']
autoapi_python_class_content = 'both'
autoapi_keep_files = True
# autoapi_generate_api_docs = False
autoapi_python_use_implicit_namespaces = True

SKIP_FULL = {'databay.link.Link._run',
             'databay.base_planner.BasePlanner._links',
             'databay.inlet.Inlet.__repr__',
             'databay.outlet.Outlet.__init__',
             'databay.outlet.Outlet.__repr__',
             'databay.planners.aps_planner.APSPlanner.__repr__',
             'databay.planners.schedule_planner.SchedulePlanner.__repr__',
             }
SKIP_SUFFIXES = {"_LOGGER"}

def maybe_skip_member(app, what, name, obj, skip, options):
    for s in SKIP_SUFFIXES:
        if s in name: return True

    return name in SKIP_FULL or skip

def setup(app):
    app.connect("autoapi-skip-member", maybe_skip_member)
    app.add_css_file('css/custom.css')


# extensions.append('sphinx_paramlinks')