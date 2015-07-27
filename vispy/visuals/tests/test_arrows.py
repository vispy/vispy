# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np

from vispy.visuals.line.arrow import ARROW_TYPES
from vispy.scene import visuals, transforms
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main, raises)
from vispy.testing.image_tester import assert_image_approved

@requires_application()
def test_line_draw():
    """Test drawing arrows without transforms"""

    vertices = np.array([
        [25, 25],
        [25, 75],
        [50, 25],
        [50, 75],
        [75, 25],
        [75, 75]
    ]).astype('f32')

    arrows = np.array([
        vertices[:2],
        vertices[3:1:-1],
        vertices[4:],
        vertices[-1:-3:-1]
    ]).reshape((4, 4))

    with TestingCanvas() as c:
        for arrow_type in ARROW_TYPES:
            arrow = visuals.Arrow(pos=vertices, arrow_type=arrow_type,
                                  arrows=arrows, arrow_size=10, color='red',
                                  connect="segments", parent=c.scene)

            assert_image_approved(c.render(), 'visuals/arrow_type_%s.png' %
                                  arrow_type)

            arrow.parent = None

run_tests_if_main()

