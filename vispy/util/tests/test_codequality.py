import sys
from nose.tools import assert_equal
from vispy.util.codequality import check_line_endings


def test_line_endings():
    """ All files should have LF line endings. """
    
    # Do not run on Windows. People might be using git's automatic
    # line ending conversion.
    if sys.platform.startswith('win'):
        return
    
    nfiles = check_line_endings()
    assert_equal(nfiles, 0)
