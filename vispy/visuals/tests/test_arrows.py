# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np

from vispy.visuals.line.arrow import ARROW_TYPES
from vispy.scene import visuals, transforms
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main, assert_raises, SkipTest, IS_TRAVIS_CI)
from vispy.testing.image_tester import assert_image_approved


vertices = np.array([
    [25, 25],
    [25, 75],
    [50, 25],
    [50, 75],
    [75, 25],
    [75, 75]
]).astype(np.float32)

vertices += 0.33

arrows = np.array([
    vertices[:2],
    vertices[3:1:-1],
    vertices[4:],
    vertices[-1:-3:-1]
]).reshape((4, 4))


@requires_application()
def test_arrow_draw():
    """Test drawing arrows without transforms"""
    with TestingCanvas() as c:
        if IS_TRAVIS_CI and c.app.backend_name.lower() == 'pyqt4':
            # TODO: Fix this (issue #1042
            raise SkipTest('Travis fails due to FB stack problem')
        for arrow_type in ARROW_TYPES:
            arrow = visuals.Arrow(pos=vertices, arrow_type=arrow_type,
                                  arrows=arrows, arrow_size=10, color='red',
                                  connect="segments", parent=c.scene)

            assert_image_approved(c.render(), 'visuals/arrow_type_%s.png' %
                                  arrow_type)

            arrow.parent = None


@requires_application()
def test_arrow_transform_draw():
    """Tests the ArrowVisual when a transform is applied"""
    with TestingCanvas() as c:
        if IS_TRAVIS_CI and c.app.backend_name.lower() == 'pyqt4':
            # TODO: Fix this (issue #1042
            raise SkipTest('Travis fails due to FB stack problem')
        for arrow_type in ARROW_TYPES:
            arrow = visuals.Arrow(pos=vertices, arrow_type=arrow_type,
                                  arrows=arrows, arrow_size=10, color='red',
                                  connect="segments", parent=c.scene)
            arrow.transform = transforms.STTransform(scale=(0.5, 0.75),
                                                     translate=(-20, -20))

            assert_image_approved(c.render(),
                                  'visuals/arrow_transform_type_%s.png' %
                                  arrow_type)

            arrow.parent = None


@requires_application()
def test_arrow_reactive():
    """Tests the reactive behaviour of the ArrowVisual properties."""
    with TestingCanvas() as c:
        arrow = visuals.Arrow(pos=vertices, arrows=arrows,
                              connect="segments", parent=c.scene)

        arrow.arrow_type = "stealth"
        assert_image_approved(c.render(), 'visuals/arrow_reactive1.png')

        arrow.arrow_size = 20
        assert_image_approved(c.render(), 'visuals/arrow_reactive2.png')


@requires_application()
def test_arrow_attributes():
    """Tests if the ArrowVisual performs the required checks for attributes."""
    with TestingCanvas() as c:
        arrow = visuals.Arrow(pos=vertices, arrow_type="stealth",
                              arrows=arrows, arrow_size=10, color='red',
                              connect="segments", parent=c.scene)

        def size_test():
            arrow.arrow_size = 0.0

        def type_test():
            arrow.arrow_type = "random_non_existent"

        assert_raises(
            ValueError, size_test
        )

        assert_raises(
            ValueError, type_test
        )


run_tests_if_main()
