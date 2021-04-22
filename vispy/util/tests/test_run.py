# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
from vispy.util import run_subprocess
from vispy.testing import run_tests_if_main, assert_raises


def test_run():
    """Test running subprocesses"""
    bad_name = 'foo_nonexist_test'
    assert_raises(Exception, run_subprocess, [bad_name])


run_tests_if_main()
