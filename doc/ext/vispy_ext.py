""" Invoke various functionality for vispy docs.
"""

import examplesgenerator
import glapigenerator
import gloooverviewgenerator


def init():
    print('Generating examples.')
    examplesgenerator.main()
    print('Generating GL API.')
    glapigenerator.main()
    print('Generating gloo overview section.')
    gloooverviewgenerator.main()


def clean(app, *args):
    examplesgenerator.clean()
    glapigenerator.clean()
    gloooverviewgenerator.clean()


def setup(app):
    init()
    app.connect('build-finished', clean)
