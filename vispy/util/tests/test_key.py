# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from vispy.util.keys import Key, ENTER
from vispy.testing import (run_tests_if_main, assert_raises, assert_true,
                           assert_equal)


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


run_tests_if_main()
