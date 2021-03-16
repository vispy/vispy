# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import gc

import numpy as np
from numpy.testing import assert_allclose

from vispy.app import Canvas
from vispy.visuals.text.text import SDFRendererCPU
from vispy.visuals.text._sdf_gpu import SDFRendererGPU
from vispy import gloo
from vispy.testing import requires_application, run_tests_if_main


@requires_application()
def test_sdf():
    """Test basic text support - sdf"""
    # test a simple case
    data = (np.array(
        [[0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 1, 1, 1, 1, 1, 0, 0],
         [0, 0, 1, 1, 1, 1, 1, 0, 0],
         [0, 0, 1, 1, 1, 1, 1, 0, 0],
         [0, 0, 1, 1, 1, 1, 1, 0, 0]]) * 255).astype(np.uint8)

    # The GPU data at one point were derived this way:
    # gpu = np.array(
    #     [[8, 5, 4, 4, 4, 4, 4, 5, 8],
    #      [5, 2, 1, 1, 1, 1, 1, 2, 5],
    #      [4, 1, 0, 0, 0, 0, 0, 1, 4],
    #      [4, 1, 0, -1, -4, -1, 0, 1, 4],  # XXX artifact
    #      [4, 1, 0, -1, -4, -1, 0, 1, 4],
    #      [4, 1, 0, -1, -4, -1, 0, 1, 4]])
    # gpu = 0.5 - (np.sqrt(np.abs(gpu)) * np.sign(gpu)) / 256. * 8
    # gpu = np.round(256 * gpu).astype(np.int)
    #
    # But it's perhaps clearer just to give what will actually be compared:
    gpu = np.array(
        [[105, 110, 112, 112, 112, 112, 112, 110, 105],
         [110, 117, 120, 120, 120, 120, 120, 117, 110],
         [112, 120, 128, 128, 128, 128, 128, 120, 112],
         [112, 120, 128, 136, 144, 136, 128, 120, 112],
         [112, 120, 128, 136, 144, 136, 128, 120, 112],
         [112, 120, 128, 136, 144, 136, 128, 120, 112]])
    cpu = np.array(
        [[0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 115, 118, 118, 118, 118, 118, 115, 0],
         [0, 118, 137, 137, 137, 137, 137, 118, 0],
         [0, 118, 137, 143, 143, 143, 137, 118, 0],
         [0, 118, 137, 143, 149, 143, 137, 118, 0],
         [0, 0, 255, 255, 255, 255, 255, 0, 0]])
    # XXX: The GPU and CPU solutions are quite different.
    #     It doesn't seem to have much effect on the visualizations but would be
    #     good to fix eventually.

    for Rend, expd in zip((SDFRendererGPU, SDFRendererCPU), (gpu, cpu)):
        with Canvas(size=(100, 100)) as c:
            tex = gloo.Texture2D(data.shape + (3,), format='rgb')
            Rend().render_to_texture(data, tex, (0, 0), data.shape[::-1])
            gloo.set_viewport(0, 0, *data.shape[::-1])
            gloo.util.draw_texture(tex)
            result = gloo.util._screenshot()[:, :, 0].astype(np.int64)
            assert_allclose(result, expd, atol=1,
                            err_msg=Rend.__name__)
            del tex, result
        del c
        # Do some garbage collection to make sure backend applications (PyQt5) actually clear things out
        gc.collect()


run_tests_if_main()
