# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
from vispy.util import run_subprocess
from vispy.testing import run_tests_if_main, assert_raises


def test_run():
    """Test running subprocesses
    """
    bad_name = 'foo_nonexist_test'
    assert_raises(Exception, run_subprocess, [bad_name])


run_tests_if_main()
