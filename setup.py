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

import numpy as np

from Cython.Build import cythonize
from setuptools import Extension, setup


extensions = [
    Extension(
        "vispy.visuals.text._sdf_cpu",
        sources=["vispy/visuals/text/_sdf_cpu.pyx"],
        include_dirs=[np.get_include()],
        define_macros=[
            ("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION"),
        ],
    )
]

setup(
    ext_modules=cythonize(extensions),
)
