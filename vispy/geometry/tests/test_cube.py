# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import numpy as np
from numpy.testing import assert_array_equal

from vispy.geometry import create_cube


def test_cube():
    """Test cube function"""
    vertices, filled, outline = create_cube()
    assert_array_equal(np.arange(len(vertices)), np.unique(filled))
    assert_array_equal(np.arange(len(vertices)), np.unique(outline))
