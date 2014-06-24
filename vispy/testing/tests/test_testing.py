from nose.tools import assert_raises
from vispy.testing import assert_in, assert_not_in, assert_is


def test_testing():
    """Test testing ports"""
    assert_raises(AssertionError, assert_in, 'foo', 'bar')
    assert_in('foo', 'foobar')
    assert_raises(AssertionError, assert_not_in, 'foo', 'foobar')
    assert_not_in('foo', 'bar')
    assert_raises(AssertionError, assert_is, None, 0)
    assert_is(None, None)
