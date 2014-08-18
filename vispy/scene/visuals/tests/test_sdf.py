# -*- coding: utf-8 -*-
import numpy as np
from numpy.testing import assert_allclose

from vispy.app import Canvas
from vispy.scene.visuals.text._sdf import SDFRenderer
from vispy import gloo
from vispy.testing import requires_application


@requires_application()
def test_text():
    """Test basic text support"""
    # test a simple cases
    data = (np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 1, 1, 1, 1, 1, 0, 0],
                      [0, 0, 1, 1, 1, 1, 1, 0, 0],
                      [0, 0, 1, 1, 1, 1, 1, 0, 0],
                      [0, 0, 1, 1, 1, 1, 1, 0, 0]]) * 255).astype(np.uint8)
    expd = (np.array([[8, 5, 4, 4, 4, 4, 4, 5, 8],
                      [5, 2, 1, 1, 1, 1, 1, 2, 5],
                      [4, 1, 0, 0, 0, 0, 0, 1, 4],
                      [4, 1, 0, -1, -4, -1, 0, 1, 4],  # XXX artifact
                      [4, 1, 0, -1, -4, -1, 0, 1, 4],
                      [4, 1, 0, -1, -4, -1, 0, 1, 4]]))
    expd = 0.5 - (np.sqrt(np.abs(expd)) * np.sign(expd)) / 256. * 8
    expd = np.round(256 * expd).astype(np.int)

    with Canvas(size=(100, 100)):
        tex = gloo.Texture2D(shape=data.shape + (3,), dtype=np.ubyte,
                             format='rgb')
        SDFRenderer().render_to_texture(data, tex, (0, 0), data.shape[::-1])
        gloo.set_viewport(0, 0, *data.shape[::-1])
        gloo.util.draw_texture(tex)
        result = gloo.util._screenshot()[:, :, 0].astype(np.int)
        print(result)
        print(expd)
        assert_allclose(result, expd, atol=1)
