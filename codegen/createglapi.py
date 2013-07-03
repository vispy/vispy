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

# We need header parser
sys.path.insert(0, THISDIR)

# Load parser
from headerparser import Parser

PREAMBLE = '''""" Classes that represent an OpenGL API. The idea is that each
class represents one opengl header file. In vispy we focus on OpenGL ES 2.0.

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


class GLApi(object):
    """ Abstract base class for OpenGL API's.
    """
    _APINAME = 'abstract'
    
    def __init__(self):
        for funcname in self._glfunctions:
            try:
                func = getattr(_GL, funcname)
            except AttributeError:
                func = self._glFuncNotAvailable
                print('warning: %s not available' % funcname )
            setattr(self, funcname, func)
    
    def _glFuncNotAvailable(self, *args, **kwargs):
        pass
        # todo: also mention what function was called
        #print('Warning: gl function not available.')
    
    def __repr__(self):
        return "<API for OpenGL %s>" % self._APINAME

'''

# Initialize lines of code
lines = []
lines.append(PREAMBLE)

# Imports
lines.append('\n')


def create_class_from_header(classname, apiname, headerfile, extension=False):
    
    # Create class that 
    parser = Parser(os.path.join(THISDIR, 'headers', headerfile))
    
    # Initialize class
    lines.append("class %s(GLApi):" % classname)
    lines.append('    """ API for OpenGL %s\n    """\n    ' % apiname)
    lines.append('    _APINAME = "%s"\n' % apiname)
    
    # Insert constants
    for c in parser.constantDefs:
        # For extensions, we only take the OES ones, and remove the OES
        if extension:
            if 'OES' in c.cname:
                c.cname = c.cname.replace('OES', '').replace('__', '_').strip('_')
            else:
                continue
        # Write constant
        if isinstance(c.value, int):
            lines.append('    %s = _GL_ENUM(%r, %r)' % (c.cname, c.cname, c.value))
        else:
            lines.append('    %s = %r' % (c.cname, c.value))
    lines.append('    ')
    
    # Insert functions
    lines.append('    _glfunctions = [')
    for f in parser.functionDefs:
        # For extensions, we only take the OES ones, and remove the OES
        if extension:
            if 'OES' in f.cname:
                f.cname = f.cname.replace('OES', '')
            else:
                continue
        # Add "super-function" if this is a group of functions
        if isinstance(f.group, list):
            if hasattr(GL, f.keyname):
                lines.append('        "%s",' % f.keyname)
        # Add line
        if hasattr(GL, f.cname):
            lines.append('        "%s",' % f.cname)
        else:
            print('WARNING: %s seems not available in PyOpenGL' % f.cname)
    lines.append('        ]')
    lines.append('    ')
    
    # Some extra empty lines
    lines.append('')
    lines.append('')
    
create_class_from_header('GLES2', 'ES 2.0', 'gl2.h')
create_class_from_header('GLES2ext', 'ES 2.0 extensions', 'gl2ext.h', True)
#create_class_from_header('GL1', '1.1 (Windows)', 'gl-1.1.h')

# Write to file
with open(os.path.join(THISDIR, '..', 'vispy', 'glapi.py'), 'wb') as f:
    f.write( '\n'.join(lines).encode('utf-8') )
