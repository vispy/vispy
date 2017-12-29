# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from vispy.util.dpi import get_dpi
from vispy.testing import run_tests_if_main


def test_dpi():
    """Test dpi support"""
    dpi = get_dpi()
    assert dpi > 0.
    assert isinstance(dpi, float)


run_tests_if_main()
