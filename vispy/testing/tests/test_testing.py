# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
from vispy.testing import (assert_in, assert_not_in, assert_is,
                           run_tests_if_main, assert_raises)


def test_testing():
    """Test testing ports"""
    assert_raises(AssertionError, assert_in, 'foo', 'bar')
    assert_in('foo', 'foobar')
    assert_raises(AssertionError, assert_not_in, 'foo', 'foobar')
    assert_not_in('foo', 'bar')
    assert_raises(AssertionError, assert_is, None, 0)
    assert_is(None, None)


run_tests_if_main()
