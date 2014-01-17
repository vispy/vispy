import numpy as np
from nose.tools import assert_equal
from numpy.testing import assert_allclose

from vispy.util.transforms import (translate, scale, xrotate, yrotate,
                                   zrotate, rotate, ortho, frustum,
                                   perspective)


def test_transforms():
    """Test basic transforms"""
    xfm = np.random.randn(4, 4)
    new_xfm = xrotate(xrotate(xfm, 90), -90)
    assert_allclose(xfm, new_xfm)
