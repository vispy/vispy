# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Vispy setup script.

Steps to do a new release:

Preparations:
  * Test on Windows, Linux, Mac
  * Make release notes
  * Update API documentation and other docs that need updating.
  * Install 'twine' package for uploading to PyPI

Define the version:
  * update __version__ in __init__.py
  * tag the tip changeset as version x.x.x; `git tag -a 'vX.Y.Z'`

Test installation:
  * clear the build and dist dir (if they exist)
  * python setup.py sdist
  * twine register --repository-url https://test.pypi.org/legacy/ dist/*
  * twine upload --repository-url https://test.pypi.org/legacy/ dist/*
  * pip install -i https://testpypi.python.org/pypi vispy

Generate and upload package
  * python setup.py sdist
  * twine register dist/*
  * twine upload dist/*

Announcing:
  * It can be worth waiting a day for eager users to report critical bugs
  * Announce in scipy-user, vispy mailing list, G+

"""

import os
from os import path as op
from warnings import warn

try:
    # use setuptools namespace, allows for "develop"
    import setuptools  # noqa, analysis:ignore
except ImportError:
    warn("unable to load setuptools. 'setup.py develop' will not work")
    pass  # it's not essential for installation
from distutils.core import setup

name = 'vispy'
description = 'Interactive visualization in Python'


# Get version and docstring
__version__ = None
__doc__ = ''
docStatus = 0  # Not started, in progress, done
initFile = os.path.join(os.path.dirname(__file__), 'vispy', '__init__.py')
for line in open(initFile).readlines():
    if (line.startswith('version_info') or line.startswith('__version__')):
        exec(line.strip())
    elif line.startswith('"""'):
        if docStatus == 0:
            docStatus = 1
            line = line.lstrip('"')
        elif docStatus == 1:
            docStatus = 2
    if docStatus == 1:
        __doc__ += line


def package_tree(pkgroot):
    path = os.path.dirname(__file__)
    subdirs = [os.path.relpath(i[0], path).replace(os.path.sep, '.')
               for i in os.walk(os.path.join(path, pkgroot))
               if '__init__.py' in i[2]]
    return subdirs


setup(
    name=name,
    version=__version__,
    author='Vispy contributors',
    author_email='vispy@googlegroups.com',
    license='(new) BSD',
    url='http://vispy.org',
    download_url='https://pypi.python.org/pypi/vispy',
    keywords="visualization OpenGl ES medical imaging 3D plotting "
             "numpy bigdata",
    description=description,
    long_description=__doc__,
    platforms='any',
    provides=['vispy'],
    install_requires=['numpy'],
    extras_require={
        'ipython-static': ['ipython'],
        'ipython-vnc': ['ipython>=2'],
        'ipython-webgl': ['ipython>=2', 'tornado'],
        'pyglet': ['pyglet>=1.2'],
        # 'pyqt4': [],  # Why is this on PyPI, but without downloads?
        # 'pyqt5': [],  # Ditto.
        'pyside': ['PySide'],
        'sdl2': ['PySDL2'],
        'wx': ['wxPython'],
    },
    packages=package_tree('vispy'),
    package_dir={
        'vispy': 'vispy'},
    package_data={
        'vispy': [op.join('io', '_data', '*'),
                  op.join('html', 'static', 'js', '*'),
                  op.join('app', 'tests', 'qt-designer.ui'),
                  ],

        'vispy.glsl': ['*.vert','*.frag', "*.glsl"],
        'vispy.glsl.antialias': ['*.vert','*.frag', "*.glsl"],
        'vispy.glsl.arrowheads': ['*.vert','*.frag', "*.glsl"],
        'vispy.glsl.arrows': ['*.vert','*.frag', "*.glsl"],
        'vispy.glsl.collections': ['*.vert','*.frag', "*.glsl"],
        'vispy.glsl.colormaps': ['*.vert','*.frag', "*.glsl"],
        'vispy.glsl.lines': ['*.vert','*.frag', "*.glsl"],
        'vispy.glsl.markers': ['*.vert','*.frag', "*.glsl"],
        'vispy.glsl.math': ['*.vert','*.frag', "*.glsl"],
        'vispy.glsl.misc': ['*.vert','*.frag', "*.glsl"],
        'vispy.glsl.transforms': ['*.vert','*.frag', "*.glsl"],

                  },
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Visualization',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: IPython'
    ],
)
