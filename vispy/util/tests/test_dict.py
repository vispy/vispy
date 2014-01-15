from os import path as op
from nose.tools import assert_true, assert_raises, assert_equal
import pickle

from vispy.util.ordereddict import OrderedDict
from vispy.util.six.moves import zip
from vispy.util import _TempDir

temp_dir = _TempDir()


def test_ordered_dict():
    """Test ordered dictionary"""
    d1 = OrderedDict()
    d2 = OrderedDict()
    for d in [d1, d2]:
        d['a'] = 1
        d['b'] = 2
        d['c'] = 3
    assert_equal(d1, d2)
    assert_true(all(dd1 == dd2
                    for dd1, dd2 in zip(reversed(d1), reversed(d2))))
    assert_raises(TypeError, OrderedDict, 1, 2)
    del d1['c']
    assert_true(d1 != d2)
    d2.popitem()
    assert_equal(d1, d2)

    # pickling (__reduce__)
    fname = op.join(temp_dir, 'pickle')
    with open(fname, 'wb') as fid:
        pickle.dump(d1, fid)
    with open(fname, 'rb') as fid:
        d1p = pickle.load(fid)
    assert_equal(d1, d1p)
