# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import logging

from vispy.util import logger, use_log_level
from vispy.testing import (assert_in, assert_not_in, run_tests_if_main,
                           assert_equal)


def test_logging():
    """Test logging context manager"""
    ll = logger.level
    with use_log_level('warning', print_msg=False):
        assert_equal(logger.level, logging.WARN)
    assert_equal(logger.level, ll)
    with use_log_level('debug', print_msg=False):
        assert_equal(logger.level, logging.DEBUG)
    assert_equal(logger.level, ll)


def test_debug_logging():
    """Test advanced debugging logging"""
    with use_log_level('debug', 'Selected', True, False) as l:
        logger.debug('Selected foo')
    assert_equal(len(l), 1)
    assert_in('test_logging', l[0])  # can't really parse this location

    with use_log_level('debug', record=True, print_msg=False) as l:
        logger.debug('foo')
    assert_equal(len(l), 1)
    assert_in('test_logging', l[0])

    with use_log_level('debug', 'foo', True, False) as l:
        logger.debug('bar')
    assert_equal(len(l), 0)

    with use_log_level('info', record=True, print_msg=False) as l:
        logger.debug('foo')
        logger.info('bar')
    assert_equal(len(l), 1)
    assert_not_in('unknown', l[0])


run_tests_if_main()
