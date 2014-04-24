import numpy as np
from numpy.testing import assert_array_equal

from vispy.util.cube import cube


def test_cube():
    """Test cube function"""
    vertices, filled, outline = cube()
    assert_array_equal(np.arange(len(vertices)), np.unique(filled))
    assert_array_equal(np.arange(len(vertices)), np.unique(outline))
