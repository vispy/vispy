"""
Readthedocs replaces some javascript sources to pull them from their own
special server. Somehow their docstools.js is incompatibe, breaking
the search tool of the docs. This hopefully fixes that.
"""

import os
import shutil

THISDIR = os.path.abspath(os.path.dirname(__file__))
HTMLDIR = os.path.join(THISDIR, '..', '_build', 'html')


def init():
    pass


def clean(app, *args):
    # Rename doctools.js
    shutil.copy(os.path.join(HTMLDIR, '_static', 'doctools.js'),
                os.path.join(HTMLDIR, '_static', 'doctools_.js'))
    # Change reference
    search_html = os.path.join(HTMLDIR, 'search.html')
    text = open(search_html, 'rt').read()
    text = text.replace('/doctools.js', '/doctools_.js')
    open(search_html, 'wt').write(text)


def setup(app):
    init()
    app.connect('build-finished', clean)
