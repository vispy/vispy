

import examplesgenerator
import glapigenerator


def init():
    print('Generating examples.')
    examplesgenerator.main()
    print('Generating GL API.')
    glapigenerator.main()

def clean(app, *args):
    examplesgenerator.clean()
    glapigenerator.clean()

def setup(app):
    init()
    app.connect('build-finished', clean)