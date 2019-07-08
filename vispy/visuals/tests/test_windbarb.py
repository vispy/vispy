# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np
from vispy.scene.visuals import Windbarb
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved

length = 15.
gridx = np.arange(length, 376, length * 2, dtype=np.float32)
gridy = np.ones_like(gridx) * length
grid = np.stack((gridx, gridy), axis=-1)
origin = (length, length)
vectors = (grid - origin).astype(np.float32)
vectors[:] /= length // 2
vectors[:, 1] *= -1


@requires_application()
def test_windbarb_draw():
    """Test drawing arrows without transforms"""
    with TestingCanvas(size=(250, 33), bgcolor='white') as c:

        Windbarb(pos=grid, wind=vectors,
                 trig=False,
                 edge_color='black',
                 face_color='black',
                 size=length, parent=c.scene)
        assert_image_approved(c.render(), 'visuals/windbarb.png')

run_tests_if_main()
