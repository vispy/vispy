# -*- coding: utf-8 -*-

from nose.tools import assert_raises

from vispy.util import run_subprocess


def test_run():
    """Test running subprocesses
    """
    bad_name = 'foo_nonexist_test'
    assert_raises(Exception, run_subprocess, [bad_name])
