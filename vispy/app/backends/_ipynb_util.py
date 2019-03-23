# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""Tools used by the IPython notebook backends."""

import re

import numpy as np

from ...ext.six import string_types, iteritems
from ...util.logs import _serialize_buffer


# -----------------------------------------------------------------------------
# GLIR commands serialization
# -----------------------------------------------------------------------------

def _extract_buffers(commands):
    """Extract all data buffers from the list of GLIR commands, and replace
    them by buffer pointers {buffer: <buffer_index>}. Return the modified list
    # of GILR commands and the list of buffers as well."""
    # First, filter all DATA commands.
    # Shader DATA commands are 3 elements, others are 4
    data_commands = [command for command in commands if command[0] == 'DATA']
    # Extract the arrays.
    buffers = [data_command[3] for data_command in data_commands]
    # Modify the commands by replacing the array buffers with pointers.
    commands_modified = list(commands)
    buffer_index = 0
    for i, command in enumerate(commands_modified):
        if command[0] == 'DATA':
            buffer = buffers[buffer_index]
            # shader code is type str; textures and everything else are numpy
            if isinstance(buffer, str):
                buffer = np.array(buffer, np.bytes_)
                buffers[buffer_index] = buffer
            commands_modified[i] = command[:3] + \
                ({'buffer_index': buffer_index,
                  'buffer_shape': buffer.shape,
                  'buffer_dtype': buffer.dtype.name},)
            buffer_index += 1
    return commands_modified, buffers


def _serialize_item(item):
    """Internal function: serialize native types."""
    # Recursively serialize lists, tuples, and dicts.
    if isinstance(item, (list, tuple)):
        return [_serialize_item(subitem) for subitem in item]
    elif isinstance(item, dict):
        return dict([(key, _serialize_item(value)) for (key, value) in iteritems(item)])

    # Serialize strings.
    elif isinstance(item, string_types):
        # Replace glSomething by something (needed for WebGL commands).
        if item.startswith('gl'):
            return re.sub(r'^gl([A-Z])', lambda m: m.group(1).lower(), item)
        else:
            return item

    # Process NumPy arrays that are not buffers (typically, uniform values).
    elif isinstance(item, np.ndarray):
        return _serialize_item(item.ravel().tolist())

    # Serialize numbers.
    else:
        try:
            # convert to scalar
            return item.item()
        except (AttributeError, ValueError):
            return item


def _serialize_command(command_modified):
    """Serialize a single GLIR (modified) command. The modification relates
    to the fact that buffers are replaced by pointers."""
    return _serialize_item(command_modified)


def create_glir_message(commands, array_serialization=None):
    """Create a JSON-serializable message of GLIR commands. NumPy arrays
    are serialized according to the specified method.

    Arguments
    ---------

    commands : list
        List of GLIR commands.
    array_serialization : string or None
        Serialization method for NumPy arrays. Possible values are:
            'binary' (default) : use a binary string
            'base64' : base64 encoded string of the array

    """
    # Default serialization method for NumPy arrays.
    if array_serialization is None:
        array_serialization = 'binary'
    # Extract the buffers.
    commands_modified, buffers = _extract_buffers(commands)
    # Serialize the modified commands (with buffer pointers) and the buffers.
    commands_serialized = [_serialize_command(command_modified)
                           for command_modified in commands_modified]
    buffers_serialized = [_serialize_buffer(buffer, array_serialization)
                          for buffer in buffers]
    # Create the final message.
    msg = {
        'msg_type': 'glir_commands',
        'commands': commands_serialized,
        'buffers': buffers_serialized,
    }
    return msg
