# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
from os import path as op
import os

from vispy.util import (config, sys_info, _TempDir, set_data_dir, save_config,
                        load_data_file)
from vispy.testing import (assert_in, requires_application, run_tests_if_main,
                           assert_raises, assert_equal, assert_true)
temp_dir = _TempDir()


@requires_application()
def test_sys_info():
    """Test printing of system information"""
    fname = op.join(temp_dir, 'info.txt')
    sys_info(fname)
    assert_raises(IOError, sys_info, fname)  # no overwrite
    with open(fname, 'r') as fid:
        out = ''.join(fid.readlines())
    keys = ['GL version', 'Python', 'Backend', 'pyglet', 'Platform:']
    for key in keys:
        assert_in(key, out)
    print(out)
    assert_true('Info-gathering error' not in out)


def test_config():
    """Test vispy config methods and file downloading"""
    assert_raises(TypeError, config.update, data_path=dict())
    assert_raises(KeyError, config.update, foo='bar')  # bad key
    data_dir = op.join(temp_dir, 'data')
    assert_raises(IOError, set_data_dir, data_dir)  # didn't say to create
    orig_val = os.environ.get('_VISPY_CONFIG_TESTING', None)
    os.environ['_VISPY_CONFIG_TESTING'] = 'true'
    try:
        assert_raises(IOError, set_data_dir, data_dir)  # doesn't exist yet
        set_data_dir(data_dir, create=True, save=True)
        assert_equal(config['data_path'], data_dir)
        config['data_path'] = data_dir
        print(config)  # __repr__
        load_data_file('CONTRIBUTING.txt')
        fid = open(op.join(data_dir, 'test-faked.txt'), 'w')
        fid.close()
        load_data_file('test-faked.txt')  # this one shouldn't download
        assert_raises(RuntimeError, load_data_file, 'foo-nonexist.txt')
        save_config()
    finally:
        if orig_val is not None:
            os.environ['_VISPY_CONFIG_TESTING'] = orig_val
        else:
            del os.environ['_VISPY_CONFIG_TESTING']


run_tests_if_main()
