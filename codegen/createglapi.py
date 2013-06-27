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

THISDIR = os.path.abspath(os.path.dirname(__file__))

# We need header parser
sys.path.insert(0, THISDIR)

# Load parser
from headerparser import Parser
parser = Parser(os.path.join(THISDIR, 'headers', 'gl2.h'))

PREAMBLE = '''""" API for OpenGL ES 2.0
This code is auto-generated. Do not edit.
"""

from OpenGL import GL as _GL

class _GL_ENUM(int):
    def __new__(cls, name, value):
        base = int.__new__(cls, value)
        base.name = name
        return base
    def __repr__( self ):
        return self.name

'''

# Initialize lines of code
lines = []
lines.append(PREAMBLE)

# Imports
lines.append('\n')

# Initialize class
lines.append('class GLApi(object):')
lines.append('    """ API for OpenGL ES 2.0\n    """')
lines.append('    ')

# Insert constants
for c in parser.constantDefs:
    if isinstance(c.value, int):
        lines.append('    %s = _GL_ENUM(%r, %r)' % (c.cname, c.cname, c.value))
    else:
        lines.append('    %s = %r' % (c.cname, c.value))
lines.append('    ')

# Insert functions
for f in parser.functionDefs:
    lines.append('    %s = _GL.%s' % (f.cname, f.cname))
lines.append('    ')

# Write to file
with open(os.path.join(THISDIR, '..', 'vispy', 'glapi.py'), 'wb') as f:
    f.write( '\n'.join(lines).encode('utf-8') )
