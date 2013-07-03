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


class GLApi(object):
    """ Abstract base class for OpenGL API's.
    """
    
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

'''

# Initialize lines of code
lines = []
lines.append(PREAMBLE)

# Imports
lines.append('\n')


CLASS_PREAMBLE = '''class %s(object):
    """ %s
    """
    
    def __init__(self):
        for funcname in self._glfunctions:
            try:
                func = getattr(_GL, funcname)
            except AttributeError:
                func = self._glFuncNotAvailable
                print('warning: %%s not available' %% funcname )
            setattr(self, funcname, func)
    
    def _glFuncNotAvailable(self, *args, **kwargs):
        pass
        # todo: also mention what function was called
        #print('Warning: gl function not available.')
    
'''


def create_class_from_header(classname, headerfile, docstring, extension=False):
    
    # Create class that 
    parser = Parser(os.path.join(THISDIR, 'headers', headerfile))
    
    # Initialize class
    lines.append("class %s(GLApi):" % classname)
    lines.append('    """ %s\n    """\n    ' % docstring)
    
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
        # Add line
        lines.append('        "%s",' % f.cname)
    lines.append('        ]')
    lines.append('    ')
    
    # Some extra empty lines
    lines.append('')
    lines.append('')
    
create_class_from_header('GLApi_es2', 'gl2.h', 'API for OpenGL ES 2.0.')
create_class_from_header('GLApi_es2_ext', 'gl2ext.h', 'API for OpenGL ES 2.0 extentions.', True)
# create_class_from_header('GLApi_1', 'gl-1.1.h', 'API for OpenGL 1.1.')

# Write to file
with open(os.path.join(THISDIR, '..', 'vispy', 'glapi.py'), 'wb') as f:
    f.write( '\n'.join(lines).encode('utf-8') )
