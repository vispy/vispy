import numpy as np
from nose.tools import assert_equal
from numpy.testing import assert_allclose

from vispy.util.transforms import (translate, scale, rotate, ortho, frustum,
                                   perspective)



def test_transforms():
    """Test basic transforms"""
    xfm = np.random.randn(4, 4).astype(np.float32)

    # Todo: this should really be more rigorous, e.g. check that the order
    # of computation is all correct
    new_xfm = rotated(90, (1,0,0)) * rotated(90, (-1, 0, 0))
    assert_allclose(xfm, new_xfm)

    new_xfm = translate((1, -1, 1)) * translate((1, -1, 1))
    assert_allclose(xfm, new_xfm)

    new_xfm = scale((1, 2, 3)) * scale((1, 1. / 2., 1. / 3.))
    assert_allclose(xfm, new_xfm)

    # These could be more complex...
    xfm = ortho(-1, 1, -1, 1, -1, 1)
    assert_equal(xfm.shape, (4, 4))

    xfm = frustum(-1, 1, -1, 1, -1, 1)
    assert_equal(xfm.shape, (4, 4))

    xfm = perspective(1, 1, -1, 1)
    assert_equal(xfm.shape, (4, 4))
