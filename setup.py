#!/usr/bin/env python

from distutils.core import setup
import sys

# get pygly's version but don't import it
# or we'll need our dependencies already installed
# https://github.com/todddeluca/happybase/commit/63573cdaefe3a2b98ece87e19d9ceb18f00bc0d9
execfile('pygly/version.py')

setup(
    name = 'pygly',
    version = __version__,
    description = 'Pure Python OpenGL framework built on top of Pyglet',
    license = 'BSD',
    author = 'Adam Griffiths',
    author_email = 'adam.lw.griffiths@gmail.com',
    url = 'https://github.com/adamlwgriffiths/PyGLy',
    requires = [
        'pyglet',
        'pyopengl',
        'pyopengl_accelerate',
        'numpy',
        'pillow',
        'pyrr',
        ],
    platforms = [ 'any' ],
    test_suite = "pygly.test",
    packages = [
        'pygly',
        'pygly.cocos2d',
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
