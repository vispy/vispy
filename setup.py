#!/usr/bin/env python

from distutils.core import setup
import sys

# get pygly's version but don't import it
# or we'll need our dependencies already installed
# https://github.com/todddeluca/happybase/commit/63573cdaefe3a2b98ece87e19d9ceb18f00bc0d9
execfile('pygly/version.py')

os_x_requires = ['pyglet(>=1.2)', 'pyobjc(==2.2)']
other_requires = ['pyglet']

setup(
    name = 'pygly',
    version = __version__,
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
