# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np
from numpy.testing import assert_array_equal

from vispy.geometry.calculations import (_bbox, _mean_center,
                                         _distance_from_point, _bsphere,
                                         _besphere)


def test_bbox():
    """Test bbox function
    """
    vertices = np.array([[0., 0., 0.], [3., 0., 0.], [0., 3., 0.]])
    bbox_res = np.array([[0., 0., 0.], [3.,  3.,  0.]])
    center_res = np.array([1., 1., 0.])
    point = np.array([0., 0., 0.])
    cdist_res = np.array([0., 3., 3.])
    center_bsphere_res = np.array([1.5,  1.5,  0.])
    # radius_bsphere_res = 2.1213203435596424

    assert_array_equal(_bbox(vertices), bbox_res)
    assert_array_equal(_mean_center(vertices), center_res)
    assert_array_equal(_distance_from_point(point, vertices), cdist_res)
    center, radius = _bsphere(vertices)
    assert_array_equal(center, center_bsphere_res)
    center, radius = _besphere(vertices)
    assert_array_equal(center, center_bsphere_res)
    # verices in 4D
    vertices = np.array([[0., 0., 0., 5.], [3., 0., 0., 5.], [0., 3., 0., 5.]])
    assert_array_equal(_bbox(vertices), bbox_res)
    assert_array_equal(_mean_center(vertices), center_res)
    assert_array_equal(_distance_from_point(point, vertices), cdist_res)
    center, radius = _bsphere(vertices)
    assert_array_equal(center, center_bsphere_res)
    center, radius = _besphere(vertices)
    assert_array_equal(center, center_bsphere_res)
