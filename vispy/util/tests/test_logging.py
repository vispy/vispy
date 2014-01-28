from nose.tools import assert_equal
import logging

from vispy.util import logger, use_log_level


def test_logging():
    """Test logging context manager"""
    ll = logger.level
    with use_log_level('warning') as u:
        assert_equal(logger.level, logging.WARN)
    assert_equal(logger.level, ll)
    with use_log_level('debug') as u:
        assert_equal(logger.level, logging.DEBUG)
    assert_equal(logger.level, ll)
