# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""Vispy setup script.

Steps to do a new release:

Preparations:
  * Test on Windows, Linux, Mac
  * Make release notes
  * Update API documentation and other docs that need updating.

Define the version and release:
  * tag the tip changeset as version x.x.x; `git tag -a 'vX.Y.Z' -m "Version X.Y.Z"`
  * push tag to github
  * verify that azure pipelines complete
  * verify that `.tar.gz` sdist and binary wheels are available on PyPI

Announcing:
  * It can be worth waiting a day for eager users to report critical bugs
  * Announce in scipy-user, vispy mailing list, twitter (@vispyproject)

"""

import os
import sys
from os import path as op
from setuptools import setup, find_packages

import numpy as np
from Cython.Build import cythonize
from Cython.Distutils import Extension

name = 'vispy'
description = 'Interactive visualization in Python'

# Special commands for building jupyter notebook extension
here = os.path.dirname(os.path.abspath(__file__))
node_root = os.path.join(here, 'js')
is_repo = os.path.exists(os.path.join(here, '.git'))

npm_path = os.pathsep.join([
    os.path.join(node_root, 'node_modules', '.bin'),
    os.environ.get('PATH', os.defpath),
])


def set_builtin(name, value):
    if isinstance(__builtins__, dict):
        __builtins__[name] = value
    else:
        setattr(__builtins__, name, value)


extensions = [Extension('vispy.visuals.text._sdf_cpu',
                        sources=[op.join('vispy', 'visuals', 'text', '_sdf_cpu.pyx')],
                        include_dirs=[np.get_include()],
                        cython_directives={"language_level": "3"},
                        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
                        ),
              ]

install_requires = ['numpy', 'freetype-py', 'hsluv', 'kiwisolver', 'packaging']
if sys.version_info < (3, 9):
    install_requires.append("importlib-resources")

readme = open('README.rst', 'r').read()
setup(
    name=name,
    use_scm_version={
        'write_to': 'vispy/version.py',
        # uses setuptools_scm.version.get_local_dirty_tag (+dirty or empty string)
        'local_scheme': 'dirty-tag',
    },
    author='Vispy contributors',
    author_email='vispy@googlegroups.com',
    license='BSD-3-Clause',
    url='http://vispy.org',
    download_url='https://pypi.python.org/pypi/vispy',
    keywords=[
        'visualization',
        'OpenGl',
        'ES',
        'medical',
        'imaging',
        '3D',
        'plotting',
        'numpy',
        'bigdata',
        'ipython',
        'jupyter',
        'widgets',
    ],
    description=description,
    long_description=readme,
    long_description_content_type='text/x-rst',
    platforms='any',
    provides=['vispy'],
    python_requires='>=3.9',
    install_requires=install_requires,
    extras_require={
        'ipython-static': ['ipython'],
        'pyglet': ['pyglet>=1.2'],
        'pyqt5': ['pyqt5'],
        'pyqt6': ['pyqt6'],
        'pyside': ['PySide'],
        'pyside2': ['PySide2'],
        'pyside6': ['PySide6'],
        'glfw': ['glfw'],
        'sdl2': ['PySDL2'],
        'wx': ['wxPython'],
        'tk': ['pyopengltk'],
        'doc': ['pydata-sphinx-theme', 'numpydoc', 'sphinxcontrib-apidoc',
                'sphinx-gallery', 'myst-parser', 'pillow', 'pytest',
                'pyopengl'],
        'io': ['meshio', 'Pillow'],
        'test': ['pytest', 'pytest-sugar', 'meshio', 'pillow', 'sphinx_gallery', 'imageio']
    },
    packages=find_packages(exclude=['make']),
    ext_modules=cythonize(extensions, language_level=3),
    package_dir={'vispy': 'vispy'},
    data_files=[],
    include_package_data=True,
    package_data={
        'vispy': [op.join('io', '_data', '*'),
                  op.join('app', 'tests', 'qt-designer.ui'),
                  op.join('util', 'fonts', 'data', '*.ttf'),
                  ],

        'vispy.glsl': ['*.vert', '*.frag', "*.glsl"],
        'vispy.glsl.antialias': ['*.vert', '*.frag', "*.glsl"],
        'vispy.glsl.arrowheads': ['*.vert', '*.frag', "*.glsl"],
        'vispy.glsl.arrows': ['*.vert', '*.frag', "*.glsl"],
        'vispy.glsl.collections': ['*.vert', '*.frag', "*.glsl"],
        'vispy.glsl.colormaps': ['*.vert', '*.frag', "*.glsl"],
        'vispy.glsl.lines': ['*.vert', '*.frag', "*.glsl"],
        'vispy.glsl.markers': ['*.vert', '*.frag', "*.glsl"],
        'vispy.glsl.math': ['*.vert', '*.frag', "*.glsl"],
        'vispy.glsl.misc': ['*.vert', '*.frag', "*.glsl"],
        'vispy.glsl.transforms': ['*.vert', '*.frag', "*.glsl"],

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
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Framework :: IPython'
    ],
)
