# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from nose.tools import assert_true

from vispy.util.dpi import get_dpi
from vispy.testing import run_tests_if_main


def test_dpi():
    """Test dpi support"""
    dpi = get_dpi()
    assert_true(dpi > 0.)
    assert_true(isinstance(dpi, float))


run_tests_if_main()
