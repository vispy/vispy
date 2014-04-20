from nose.tools import assert_raises, assert_true, assert_equal

from vispy.util.keys import Key, ENTER


def test_key():
    """Test basic key functionality"""
    def bad():
        return (ENTER == dict())
    assert_raises(ValueError, bad)
    assert_true(not (ENTER == None))  # noqa
    assert_equal('Return', ENTER)
    print(ENTER.name)
    print(ENTER)  # __repr__
    assert_equal(Key('1'), 49)  # ASCII code
