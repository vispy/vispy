# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np
from numpy.testing import assert_allclose

from vispy import scene
from vispy.testing import (TestingCanvas, requires_application,
                           requires_pyopengl, run_tests_if_main)
from vispy.testing.image_tester import assert_image_reasonable


@requires_pyopengl()
@requires_application()
def test_gridmesh_shading():
    """Test GridMesh smooth shading matches flat shading on planar grid."""
    # Regression test for gh-2606
    xs, zs = np.meshgrid(np.linspace(-2, 2, 10), np.linspace(-2, 2, 10),
                         indexing='ij')
    ys = np.zeros_like(xs)

    rendered = {}
    for shading in ('flat', 'smooth'):
        with TestingCanvas(size=(120, 100), bgcolor='w') as c:
            view = c.central_widget.add_view()
            view.camera = 'arcball'
            mesh = scene.visuals.GridMesh(xs, ys, zs, shading=shading)
            view.add(mesh)
            view.camera.set_range()
            rendered[shading] = c.render()

    assert_image_reasonable(rendered['smooth'])
    assert_allclose(rendered['smooth'], rendered['flat'], atol=2)

    fg_pixels = rendered['smooth'][
        np.any(rendered['smooth'][:, :, :3] != 255, axis=2)
    ][:, :3]
    assert len(fg_pixels) > 0
    assert np.all(np.ptp(fg_pixels, axis=0) <= 2)


run_tests_if_main()
