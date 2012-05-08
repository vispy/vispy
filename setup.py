#!/usr/bin/env python

from distutils.core import setup

setup(
    name = 'PyGLy',
    version = '20120506',
    description = 'Pyglet based 3D Framework',
    long_description = """An OpenGL framework designed for flexbility
        and power. PyGLy provides a number of tools to let you
        do what you want, how you want.""",
    license = 'BSD',
    author = 'Adam Griffiths',
    author_email = 'adam.lw.griffiths@gmail.com',
    url = 'https://github.com/adamlwgriffiths/PyGLy',
    platforms = [ 'any' ],
    packages = [
        'pygly',
        'pygly.cocos2d',
        'pygly.common',
        'pygly.helpers',
        'pygly.input',
        'pygly.mesh',
        'pygly.mesh.uv_generators',
        'pygly.renderer'
        'pygly.scene',
        ],
    classifiers = [
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Multimedia :: Graphics :: 3D Rendering',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ]
    )
