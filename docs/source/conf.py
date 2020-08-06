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
from setuptools import find_packages
from pkgutil import iter_modules
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
    'sphinx.ext.viewcode',
    # 'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    # 'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

# autosummary_generate = True

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

import sphinx_rtd_theme

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
autoapi_ignore = [
    # '*databay/__init__.py',
    # '/*test*/',
    '*examples/*',
    '*misc/*',
    # '*inlets/random_int_inlet.py',
    # '*outlets/print_outlet.py',
    # '*outlets/csv_outlet.py',
    '*config.py',
  ]
autoapi_options = [ 'members', 'undoc-members', 'xprivate-members', 'show-inheritance', 'show-module-summary', 'xspecial-members', 'ximported-members']
autoapi_python_class_content = 'both'
autoapi_keep_files = True

if not os.getenv('READTHEDOCS'):
    autoapi_generate_api_docs = False
    autoapi_generate_api_docs = True

autoapi_python_use_implicit_namespaces = True


SKIP_FULL = {'databay.link.Link._run',
             'databay.base_planner.BasePlanner._links',
             'databay.inlets.HttpInlet',
             'databay.outlet.metadata',
             # 'databay.inlet.Inlet.__repr__',
             'databay.outlets.MongoOutlet',
             # 'databay.outlet.Outlet.__init__',
             # 'databay.outlet.Outlet.__repr__',
             # 'databay.planners.aps_planner.APSPlanner.__repr__',
             # 'databay.planners.schedule_planner.SchedulePlanner.__repr__',
             }
SKIP_SUFFIXES = {"_LOGGER"}

def maybe_skip_member(app, what, name, obj, skip, options):
    should_skip = skip
    for s in SKIP_SUFFIXES:
        if s in name:
            should_skip = True
            break

    should_skip = name in SKIP_FULL or should_skip

    if not should_skip and what == 'module':
        populate_modules(None, name)

    return should_skip



def find_modules(path):
    package_name = path.replace('../', '').replace('\\', '.')
    modules = set()

    for info in iter_modules([path]):
        if not info.ispkg:
            modules.add(package_name + '.' + info.name)


    for pkg in find_packages(path):
        ms = find_modules(os.path.join(path, pkg))
        modules.update(ms)

    return modules

# modules = find_modules('../../databay')

this_filedir = os.path.dirname(os.path.abspath(__file__))

source_code_filepath = os.path.join(this_filedir, '_modules', 'index.rst')
source_code_contents = """
.. _source_code:

Source Code
===========

.. toctree::
  :maxdepth: 1

"""

modules_complete = {}

def populate_modules(_, fqp):
    if len(modules_complete) == 0 :
        # init the index file
        with open(source_code_filepath, 'w') as f:
            f.write(source_code_contents)

    if fqp in modules_complete:
        return None
    else:
        modules_complete[fqp] = True

    chunks = fqp.split('.')
    dirs = chunks[:-1]
    module = chunks[-1]
    filename =  module+'.rst'
    filepath = os.path.abspath(os.path.join(this_filedir, '_modules', *dirs, filename))
    dir = os.path.dirname(filepath)
    os.makedirs(dir, exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(f'{module}\n{"-"*len(module)}')

    # if len(dirs) > 1:
    with open(source_code_filepath, 'a') as f:
        f.write(f'  {module} <{fqp.replace(".", "/")}>\n')

    return None

extensions.append('sphinx_copybutton')


def setup(app):
    app.connect("autoapi-skip-member", maybe_skip_member)
    app.add_css_file('css/custom.css')
