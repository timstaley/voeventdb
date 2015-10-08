# -*- coding: utf-8 -*-
#
# voeventcache documentation build configuration file, created by
# sphinx-quickstart on Tue Oct  6 14:09:26 2015.
#

# -- General configuration ------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinxcontrib.httpdomain',
    'sphinxcontrib.autohttp.flask',

]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'voeventcache'
copyright = u'2015, Tim Staley'
author = u'Tim Staley'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '0.1a0'
# The full version, including alpha/beta/rc tags.
release = '0.1a0'

language = None


# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# Output file base name for HTML help builder.
htmlhelp_basename = 'voeventcachedoc'


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'voeventcache', u'voeventcache Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
  (master_doc, 'voeventcache', u'voeventcache Documentation',
   author, 'voeventcache', 'One line description of project.',
   'Miscellaneous'),
]



# Ugly hack to fix the endpoint sorting:
# We overwrite the 'get_routes' function with a subtly altered version
# This is essentially a copy-paste, but with the ``iter_rules`` call
# wrapped by a ``sorted``.
# Written against sphinxcontrib-httpdomain==1.4.0 (as per requirements.txt).
import sphinxcontrib.autohttp.flask as autodocflask

def get_routes(app, endpoint=None):
    endpoints = []
    for rule in sorted(app.url_map.iter_rules(endpoint)):
        if rule.endpoint not in endpoints:
            endpoints.append(rule.endpoint)
    for endpoint in endpoints:
        methodrules = {}
        for rule in app.url_map.iter_rules(endpoint):
            methods = rule.methods.difference(['OPTIONS', 'HEAD'])
            path = autodocflask.translate_werkzeug_rule(rule.rule)
            for method in methods:
                if method in methodrules:
                    methodrules[method].append(path)
                else:
                    methodrules[method] = [path]
        for method, paths in methodrules.items():
            yield method, paths, endpoint

autodocflask.get_routes = get_routes