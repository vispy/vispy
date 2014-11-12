# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""Serialization tools used by the IPython notebook backends."""

import re
import base64

import numpy as np

from ..ext.six import string_types


# -----------------------------------------------------------------------------
# GLIR commands serialization
# -----------------------------------------------------------------------------

def _extract_buffers(commands):
    """Extract all data buffers from the list of GLIR commands, and replace
    them by buffer pointers {buffer: <buffer_index>}. Return the modified list
    # of GILR commands and the list of buffers as well."""
    # First, filter all DATA commands.
    data_commands = [command for command in commands if command[0] == 'DATA']
    # Extract the arrays.
    buffers = [data_command[3] for data_command in data_commands]
    # Modify the commands by replacing the array buffers with pointers.
    commands_modified = commands.copy()
    buffer_index = 0
    for i, command in enumerate(commands_modified):
        if command[0] == 'DATA':
            commands_modified[i] = command[:3] + \
                ({'buffer_index': buffer_index},)
            buffer_index += 1
    return commands_modified, buffers


def _serialize_command(command_modified):
    """Serialize a single GLIR (modified) command. The modification relates
    to the fact that buffers are replaced by pointers."""
    # TODO
    return


def create_glir_message(commands):
    commands_modified, buffers = _extract_buffers(commands)
    commands_serialized = [_serialize_command(command_modified)
                           for command_modified in commands_modified]
    msg = {
        'msg_type': 'glir_commands',
        'commands': commands_serialized,
        'buffers': buffers,
    }
    return msg


def _serializable(c, serialize_array=True):
    if isinstance(c, list):
        return [_serializable(command, serialize_array=serialize_array)
                for command in c]
    if isinstance(c, tuple):
        if c and c[0] == 'UNIFORM':
            serialize_array = False
        return list(_serializable(command, serialize_array=serialize_array)
                    for command in c)
    elif isinstance(c, np.ndarray):
        if serialize_array:
            # TODO: binary websocket (once the IPython PR has been merged)
            return {
                'storage_type': 'base64',
                'buffer': base64.b64encode(c).decode('ascii'),
            }
        else:
            return _serializable(c.ravel().tolist(), False)
    elif isinstance(c, string_types):
        # replace glSomething by something (needed for WebGL commands)
        if c.startswith('gl'):
            return re.sub(r'^gl([A-Z])', lambda m: m.group(1).lower(), c)
        else:
            return c
    else:
        try:
            return np.asscalar(c)
        except Exception:
            return c
