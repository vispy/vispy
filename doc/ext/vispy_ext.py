""" Invoke various functionality for vispy docs.
"""

import examplesgenerator
import glapigenerator
import oogloverviewgenerator


def init():
    print('Generating examples.')
    examplesgenerator.main()
    print('Generating GL API.')
    glapigenerator.main()
    print('Generating oogl overview section.')
    oogloverviewgenerator.main()


def clean(app, *args):
    examplesgenerator.clean()
    glapigenerator.clean()
    oogloverviewgenerator.clean()


def setup(app):
    init()
    app.connect('build-finished', clean)
