# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Script to create an OpenGL ES 2.0 API

The header file for the OpenGL ES standard is parsed to obtain a list
of constants and functions.

At this point, the constants are fully parsed by ourselves, but for the
functions we inject the corresponding function of PyOpenGL. Later on,
we may create functions that hook into the OpenGL library themselves,
or that pipe the OpenGL commands to elsewhere, such as a WebGL instance.

"""

import os
import sys

from OpenGL import GL

THISDIR = os.path.abspath(os.path.dirname(__file__))
GLDIR = os.path.join(THISDIR, '..', 'vispy', 'gloo', 'gl')


# We need header parser
sys.path.insert(0, THISDIR)

# Load parser
from headerparser import Parser

PREAMBLE = '''"""

THIS CODE IS AUTO-GENERATED. DO NOT EDIT.

%s

"""
'''


def create_constants_module(parser, extension=False):

    # Initialize
    lines = []
    lines.append(PREAMBLE % 'Constants for OpenGL ES 2.0.')

    # __future__ import
    lines.append(
        'from __future__ import print_function, division, absolute_import\n')

    # Import enum
    lines.append('from . import _GL_ENUM')
    lines.append('\n')

    # For extensions, we only take the OES ones, and remove the OES
    if extension:
        constantDefs = []
        for c in parser.constantDefs:
            if 'OES' in c.cname:
                c.cname = c.cname.replace(
                    'OES',
                    '').replace(
                    '__',
                    '_').strip('_')
                constantDefs.append(c)
    else:
        constantDefs = parser.constantDefs

    # Insert constants
    for c in sorted(constantDefs, key=lambda x: x.cname):
        if isinstance(c.value, int):
            lines.append('%s = _GL_ENUM(%r, %r)' % (c.cname, c.cname, c.value))
        else:
            lines.append('%s = %r' % (c.cname, c.value))
    lines.append('')

    # Write the file
    fname = '_constants_ext.py' if extension else '_constants.py'
    with open(os.path.join(GLDIR, fname), 'w') as f:
        f.write('\n'.join(lines))
    print('wrote %s' % fname)


def create_desktop_module(parser, extension=False):

    # Initialize
    lines = []
    doc = 'OpenGL ES 2.0 API based on desktop OpenGL (via pyOpenGL).'
    lines.append(PREAMBLE % doc)

    # __future__ import
    lines.append(
        'from __future__ import print_function, division, absolute_import\n')

    # Import constants and ext
    if extension:
        lines.append('from ._constants_ext import *')
    else:
        lines.append('from ._constants import *')

    lines.append('\n')

    # For extensions, we only take the OES ones, and remove the OES
    if extension:
        functionDefs = []
        for f in parser.functionDefs:
            if 'OES' in f.cname:
                f.cname = f.cname.replace('OES', '')
                functionDefs.append(f)
    else:
        functionDefs = parser.functionDefs

    # Insert functions
    lines.append('_glfunctions = [')
    for f in sorted(functionDefs, key=lambda x: x.cname):
        # Add "super-function" if this is a group of functions
        if isinstance(f.group, list):
            if hasattr(GL, f.keyname):
                lines.append('    "%s",' % f.keyname)
        # Add line
        if hasattr(GL, f.cname):
            lines.append('    "%s",' % f.cname)
        else:
            print('WARNING: %s seems not available in PyOpenGL' % f.cname)
    lines.append('    ]')

    lines.append('')

    # Write the file
    fname = '_desktop_ext.py' if extension else '_desktop.py'
    with open(os.path.join(GLDIR, fname), 'w') as f:
        f.write('\n'.join(lines))
    print('wrote %s' % fname)


if __name__ == '__main__':
    # Create code  for normal ES 2.0
    parser = Parser(os.path.join(THISDIR, 'headers', 'gl2.h'))
    create_constants_module(parser)
    create_desktop_module(parser)

    # Create code for extensions
    parser = Parser(os.path.join(THISDIR, 'headers', 'gl2ext.h'))
    create_constants_module(parser, True)
    create_desktop_module(parser, True)
