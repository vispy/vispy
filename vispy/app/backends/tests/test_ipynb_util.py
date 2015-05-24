# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import numpy as np

from vispy.app.backends._ipynb_util import (_extract_buffers,
                                            _serialize_command,
                                            create_glir_message)
from vispy.testing import run_tests_if_main, assert_equal


def test_extract_buffers():
    arr = np.random.rand(10, 2).astype(np.float32)
    arr2 = np.random.rand(20, 2).astype(np.int16)

    # No DATA command.
    commands = [('CREATE', 4, 'VertexBuffer')]
    commands_modified, buffers = _extract_buffers(commands)
    assert_equal(commands_modified, commands)
    assert_equal(buffers, [])

    # A single DATA command.
    commands = [('DATA', 4, 0, arr)]
    commands_modified, buffers = _extract_buffers(commands)
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
    commands_modified, buffers = _extract_buffers(commands)
    assert_equal(commands_modified, commands_modified_expected)
    assert_equal(buffers, [arr, arr2])


def test_serialize_command():
    command = ('CREATE', 4, 'VertexBuffer')
    command_serialized = _serialize_command(command)
    assert_equal(command_serialized, list(command))

    command = ('UNIFORM', 4, 'u_scale', 'vec3', (1, 2, 3))
    commands_serialized_expected = ['UNIFORM', 4, 'u_scale', 'vec3', [1, 2, 3]]
    command_serialized = _serialize_command(command)
    assert_equal(command_serialized, commands_serialized_expected)


def test_create_glir_message_binary():
    arr = np.zeros((3, 2)).astype(np.float32)
    arr2 = np.ones((4, 5)).astype(np.int16)

    commands = [('CREATE', 1, 'VertexBuffer'),
                ('UNIFORM', 2, 'u_scale', 'vec3', (1, 2, 3)),
                ('DATA', 3, 0, arr),
                ('UNIFORM', 4, 'u_pan', 'vec2', np.array([1, 2, 3])),
                ('DATA', 5, 20, arr2)]
    msg = create_glir_message(commands)
    assert_equal(msg['msg_type'], 'glir_commands')

    commands_serialized = msg['commands']
    assert_equal(commands_serialized,
                 [['CREATE', 1, 'VertexBuffer'],
                  ['UNIFORM', 2, 'u_scale', 'vec3', [1, 2, 3]],
                  ['DATA', 3, 0, {'buffer_index': 0}],
                  ['UNIFORM', 4, 'u_pan', 'vec2', [1, 2, 3]],
                  ['DATA', 5, 20, {'buffer_index': 1}]])

    buffers_serialized = msg['buffers']
    buf0 = buffers_serialized[0]
    assert_equal(buf0, b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')  # noqa

    buf1 = buffers_serialized[1]
    assert_equal(buf1, b'\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00')  # noqa


def test_create_glir_message_base64():
    arr = np.zeros((3, 2)).astype(np.float32)
    arr2 = np.ones((4, 5)).astype(np.int16)

    commands = [('CREATE', 1, 'VertexBuffer'),
                ('UNIFORM', 2, 'u_scale', 'vec3', (1, 2, 3)),
                ('DATA', 3, 0, arr),
                ('UNIFORM', 4, 'u_pan', 'vec2', np.array([1, 2, 3])),
                ('DATA', 5, 20, arr2)]
    msg = create_glir_message(commands, array_serialization='base64')
    assert_equal(msg['msg_type'], 'glir_commands')

    commands_serialized = msg['commands']
    assert_equal(commands_serialized,
                 [['CREATE', 1, 'VertexBuffer'],
                  ['UNIFORM', 2, 'u_scale', 'vec3', [1, 2, 3]],
                  ['DATA', 3, 0, {'buffer_index': 0}],
                  ['UNIFORM', 4, 'u_pan', 'vec2', [1, 2, 3]],
                  ['DATA', 5, 20, {'buffer_index': 1}]])

    buffers_serialized = msg['buffers']
    buf0 = buffers_serialized[0]
    assert_equal(buf0['storage_type'], 'base64')
    assert_equal(buf0['buffer'], 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')

    buf1 = buffers_serialized[1]
    assert_equal(buf0['storage_type'], 'base64')
    assert_equal(buf1['buffer'],
                 'AQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAEAAQABAA==')


run_tests_if_main()
