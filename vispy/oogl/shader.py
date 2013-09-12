# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2013, Vispy Development Team. All rights reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
VertexShader and FragmentShader classes.

These classes are almost never created explicitly but are created implicitly
from within a Program object.

Example
-------

  vert = "some code"
  frag = "some code"

  program = Program(vert,frag)
"""
from __future__ import print_function, division

import re
import os.path
import numpy as np
import OpenGL.GL as gl

from vispy import gl
from vispy.util import is_string
from vispy.oogl.globject import GLObject



# ------------------------------------------------------- class ShaderError ---
class ShaderError(RuntimeError):
    """ Shader error class """
    pass





# ------------------------------------------------------------ class Shader ---
class Shader(GLObject):
    """
    Abstract shader class.
    """

    # Conversion of known uniform and attribute types to GL constants
    _gtypes = {
        'float':       gl.GL_FLOAT,
        'vec2':        gl.GL_FLOAT_VEC2,
        'vec3':        gl.GL_FLOAT_VEC3,
        'vec4':        gl.GL_FLOAT_VEC4,
        'int':         gl.GL_INT,
        'ivec2':       gl.GL_INT_VEC2,
        'ivec3':       gl.GL_INT_VEC3,
        'ivec4':       gl.GL_INT_VEC4,
        'bool':        gl.GL_BOOL,
        'bvec2':       gl.GL_BOOL_VEC2,
        'bvec3':       gl.GL_BOOL_VEC3,
        'bvec4':       gl.GL_BOOL_VEC4,
        'mat2':        gl.GL_FLOAT_MAT2,
        'mat3':        gl.GL_FLOAT_MAT3,
        'mat4':        gl.GL_FLOAT_MAT4,
        'sampler2D':   gl.GL_SAMPLER_2D,
        'sampler3D':   gl.ext.GL_SAMPLER_3D,
        'samplerCube': gl.GL_SAMPLER_CUBE }
    
    
    def __init__(self, target, code=None):
        """
        Create the shader and store code.
        """

        GLObject.__init__(self)
        
        # Check and store target
        if target not in [gl.GL_VERTEX_SHADER, gl.GL_FRAGMENT_SHADER]:
            raise ValueError('Target must be vertex or fragment shader.')
        self._target = target
        
        # Set code
        self._code = None
        self._source = None
        if code is not None:
            self.code = code
    
    
    def _set_code(self, code, source=None):
        # Otherwise we cannot proprly test this class
        self.code = code
        self._source = source
    
    # todo: mmm, this is I think the *only* settable property in oogl, turn into method?
    
    @property
    def code(self):
        """
        The actual code of the shader.
        """
        
        return self._code
    
    @code.setter
    def code(self, code):
        """
        Set the code of the shader.
        """

        if not is_string(code):
            raise TypeError('code must be a string (%s)' % type(code))
        # Set code and source
        if os.path.exists(code):
            with open(code) as file:
                self._code   = file.read()
                self._source = os.path.basename(code)
        else:
            self._code   = code
            self._source = '<string>'

        # Set flags
        self._need_update = True

    
    @property
    def source(self):
        """
        The source of the code for this shader (not the source code).
        """

        return self._source
    
    
    def _get_attributes(self):
        """
        Extract attributes (name and type) from code.
        """

        attributes = []
        regex = re.compile("""\s*attribute\s+(?P<type>\w+)\s+"""
                           """(?P<name>\w+)\s*(\[(?P<size>\d+)\])?\s*;""")
        for m in re.finditer(regex,self._code):
            size = -1
            gtype = Shader._gtypes[m.group('type')]
            if m.group('size'):
                size = int(m.group('size'))
            if size >= 1:
                for i in range(size):
                    name = '%s[%d]' % (m.group('name'),i)
                    attributess.append((name, gtype))
            else:
                attributes.append((m.group('name'), gtype))

        return attributes
    
    
    def _get_uniforms(self):
        """
        Extract uniforms (name and type) from code.
        """

        uniforms = []
        regex = re.compile("""\s*uniform\s+(?P<type>\w+)\s+"""
                           """(?P<name>\w+)\s*(\[(?P<size>\d+)\])?\s*;""")
        for m in re.finditer(regex,self._code):
            size = -1
            gtype = Shader._gtypes[m.group('type')]
            if m.group('size'):
                size = int(m.group('size'))
            if size >= 1:
                for i in range(size):
                    name = '%s[%d]' % (m.group('name'),i)
                    uniforms.append((name, gtype))
            else:
                uniforms.append((m.group('name'), gtype))

        return uniforms
    
    
    def _create(self):
        """
        Create the shader.
        """
        self._handle = gl.glCreateShader(self._target)
    
    
    def _delete(self):
        """
        Delete the shader.
        """

        gl.glDeleteShader(self._handle)

    
    def _update(self):
        """
        Compile the shader.
        """

        # Check if we have source code
        if not self._code:
            raise ShaderError('No source code given for shader.')
        
        # Set source
        gl.glShaderSource(self._handle, self._code)
        
        # Compile the shader
        # todo: can this raise exception?
        gl.glCompileShader(self._handle)

        # Check the compile status
        status = gl.glGetShaderiv(self._handle, gl.GL_COMPILE_STATUS)
        if not status:
            print( "Error compiling shader %r" % self )
            errors = gl.glGetShaderInfoLog(self._handle)
            self._parse_shader_errors(errors, self._code)
            raise ShaderError("Shader compilation error")


    def _parse_error(self, error):
        """
        Parses a single GLSL error and extracts the line number and error
        description.

        Parameters
        ----------
        error : str
            An error string as returned byt the compilation process
        """

        # Nvidia
        # 0(7): error C1008: undefined variable "MV"
        m = re.match(r'(\d+)\((\d+)\):\s(.*)', error )
        if m: return int(m.group(2)), m.group(3)

        # ATI / Intel
        # ERROR: 0:131: '{' : syntax error parse error
        m = re.match(r'ERROR:\s(\d+):(\d+):\s(.*)', error )
        if m: return int(m.group(2)), m.group(3)

        # Nouveau
        # 0:28(16): error: syntax error, unexpected ')', expecting '('
        m = re.match( r'(\d+):(\d+)\((\d+)\):\s(.*)', error )
        if m: return int(m.group(2)), m.group(4)

        raise ValueError('Unknown GLSL error format')


    def _print_error(self, error, lineno):
        """
        Print error and show the faulty line + some context

        Parameters
        ----------
        error : str
            An error string as returned byt the compilation process

        lineno: int
            Line where error occurs
        """
        lines = self._code.split('\n')
        start = max(0,lineno-2)
        end = min(len(lines),lineno+1)

        print('Error in %s' % (repr(self)))
        print(' -> %s' % error)
        print()
        if start > 0:
            print(' ...')
        for i, line in enumerate(lines[start:end]):
            if (i+start) == lineno:
                print(' %03d %s' % (i+start, line))
            else:
                if len(line):
                    print(' %03d %s' % (i+start,line))
        if end < len(lines):
            print(' ...')
        print()




# ------------------------------------------------------ class VertexShader ---
class VertexShader(Shader):
    """
    Vertex shader class.
    """

    def __init__(self, code=None):
        """
        Create the shader.
        """

        Shader.__init__(self, gl.GL_VERTEX_SHADER, code)


    def __repr__(self):
        """
        x.__repr__() <==> repr(x)
        """

        return "Vertex Shader %d (%s)" % (self._id, self._source)





# ---------------------------------------------------- class FragmentShader ---
class FragmentShader(Shader):
    """
    Fragment shader class
    """

    def __init__(self, code=None):
        """
        Create the shader.
        """

        Shader.__init__(self, gl.GL_FRAGMENT_SHADER, code)


    def __repr__(self):
        """
        x.__repr__() <==> repr(x)
        """

        return "Vertex Shader %d (%s)" % (self._id, self._source)
