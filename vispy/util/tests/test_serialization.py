# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import numpy as np
from nose.tools import assert_equal

from vispy.util import serialization
from vispy.testing import run_tests_if_main


def test_extract_buffers():
    arr = np.random.rand(10, 2).astype(np.float32)
    arr2 = np.random.rand(20, 2).astype(np.int16)

    # No DATA command.
    commands = [('CREATE', 4, 'VertexBuffer')]
    commands_modified, buffers = serialization._extract_buffers(commands)
    assert_equal(commands_modified, commands)
    assert_equal(buffers, [])

    # A single DATA command.
    commands = [('DATA', 4, 0, arr)]
    commands_modified, buffers = serialization._extract_buffers(commands)
    assert_equal(commands_modified, [('DATA', 4, 0, {'buffer_index': 0})])
    assert_equal(buffers, [arr])

    # Several commands.
    commands = [('DATA', 0, 10, arr),
                ('UNIFORM', 4, 'u_scale', 'vec3', (1, 2, 3)),
                ('DATA', 2, 20, arr2)
                ]
    commands_modified_expected = [
        ('DATA', 0, 10, {'buffer_index': 0}),
        ('UNIFORM', 4, 'u_scale', 'vec3', (1, 2, 3)),
        ('DATA', 2, 20, {'buffer_index': 1})]
    commands_modified, buffers = serialization._extract_buffers(commands)
    assert_equal(commands_modified, commands_modified_expected)
    assert_equal(buffers, [arr, arr2])

run_tests_if_main()
