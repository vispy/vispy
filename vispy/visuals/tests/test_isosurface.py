# -*- coding: utf-8 -*-

import numpy as np
from vispy import scene

from vispy.testing import run_tests_if_main, requires_pyopengl


@requires_pyopengl()
def test_isosurface():

    # Create data
    vol = np.arange(1000).reshape((10, 10, 10)).astype(np.float32)

    # Create visual
    iso = scene.visuals.Isosurface(vol, level=200)

    # Change color (regression test for a bug that caused this to crash)
    iso.color = (1.0, 0.8, 0.9, 1.0)


run_tests_if_main()
