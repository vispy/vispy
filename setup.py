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
