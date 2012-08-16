#!/usr/bin/env python

from distutils.core import setup
import sys

import pygly

os_x_requires = ['pyglet(>=1.2)', 'pyobjc(==2.2)']
other_requires = ['pyglet']

setup(
    name = 'pygly',
    version = pygly.__version__,
    description = 'Pyglet based 3D Framework',
    long_description = """An OpenGL framework designed for flexbility
        and power. PyGLy provides a number of tools to let you
        do what you want, how you want.""",
    license = 'BSD',
    author = 'Adam Griffiths',
    author_email = 'adam.lw.griffiths@gmail.com',
    url = 'https://github.com/adamlwgriffiths/PyGLy',
    requires = [
        'numpy',
        'cython',
        'pil',
        'pyrr',
        ]
        + (
            os_x_requires if 'darwin' in sys.platform else other_requires
            ),
    platforms = [ 'any' ],
    test_suite = "pygly.test",
    packages = [
        'pygly',
        'pygly.cocos2d',
        'pygly.input',
        'pygly.mesh',
        'pygly.uv_generators',
        ],
    classifiers = [
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: 3D Rendering',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ]
    )
