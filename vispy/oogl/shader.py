# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Definition of shader classes.

This code is inspired by similar classes from Pygly.

"""

from __future__ import print_function, division, absolute_import

import os
import sys
import re

import numpy as np

from vispy import gl
from vispy.util.six import string_types, text_type
from . import GLObject, ext_available


class ShaderError(RuntimeError):
    """ Raised when something goes wrong that depens on state that was set 
    earlier (due to deferred loading).
    """
    pass


class Shader(GLObject):
    """ Abstract shader class.
    """
    
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
        'samplerCube': gl.GL_SAMPLER_CUBE
    }
    
    
    def __init__(self, target, code=None):
        GLObject.__init__(self)
        
        # Check and store target
        if target not in [gl.GL_VERTEX_SHADER, gl.GL_FRAGMENT_SHADER]:
            raise ValueError('Target must be vertex or fragment shader.')
        self._target = target
        
        self._description = None
        
        # Set code
        self._code = None
        self._source = None
        if code is not None:
            self.set_code(code)
    
    
    def set_code(self, code, source=None):
        """ Set the source of the shader.
        """
        if not isinstance(code, string_types):
            raise TypeError('code argument must be string (%s)' % type(code))
        # Set code and source
        if os.path.exists(code):
            with open(code) as file:
                self._code   = file.read()
                self._source = os.path.basename(code)
        else:
            self._code   = code
            self._source = text_type(source) if (source is not None) else '<string>'
        # Set flags
        self._need_update = True  # Make _update be called
        self._description = None
    
    
    @property
    def code(self):
        """ The code for this Shader.
        """
        return self._code
    
    
    @property
    def source(self):
        """ The source of the code for this shader (not the source code).
        """
        return self._source
    
    
    def add_source(self, source):
        """ Templating, for later?
        """
        raise NotImplemented()
    
    
    def __repr__(self):
        if self._description is None:
            # Try to get description from beginning of source
            if self._code is None:
                self._description = hex(id(self))
            else:
                for line in self._code.split('\n'):
                    line = line.strip(' \t')
                    if line == '':
                        continue
                    if line.startswith('/'):
                        self._description = line.strip(' \t/*')
                        break
                    else:
                        self._description = hex(id(self))
                        break
            
        return "<%s '%s'>" % (self.__class__.__name__, self._description)
    
    
    def _get_attributes(self):
        """ Extract attributes (name and type) from code
        Used by Program.
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
        """ Extract uniforms (name and type) from code
        Used by Program.
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
    
    
    ## Be a good GLObject
    
    def _create(self):
        self._handle = gl.glCreateShader(self._target)
    
    
    def _delete(self):
        gl.glDeleteShader(self._handle)
    
    
    def _activate(self):
        pass
    
    
    def _dactivate(self):
        pass
    
    
    def _update(self):
        
        # Check if we have source code
        if not self._code:
            raise RuntimeError('No source code given for shader.')
        
        # Set source
        gl.glShaderSource(self._handle, self._code)
        
        # Compile the shader
        # todo: can this raise exception?
        gl.glCompileShader(self._handle)

        # Check the compile status
        if not gl.glGetShaderiv(self._handle, gl.GL_COMPILE_STATUS):
            print( "Error compiling shader %r" % self )
            errors = gl.glGetShaderInfoLog(self._handle)
            parse_shader_errors(errors, self._code)
            raise ShaderError("Shader compilation error")



class VertexShader(Shader):
    """ Representation of a vertex shader object. Inherits BaseShader.
    """
    def __init__(self, source=None):
        Shader.__init__(self, gl.GL_VERTEX_SHADER, source)



class FragmentShader(Shader):
    """ Representation of a fragment shader object. Inherits BaseShader.
    """
    def __init__(self, source=None):
        Shader.__init__(self, gl.GL_FRAGMENT_SHADER, source)



def parse_shader_error(error):
    """Parses a single GLSL error and extracts the line number
    and error description.

    Line number and description are returned as a tuple.

    GLSL errors are not defined by the standard, as such,
    each driver provider prints their own error format.

    Nvidia print using the following format::

        0(7): error C1008: undefined variable "MV"

    Nouveau Linux driver using the following format::

        0:28(16): error: syntax error, unexpected ')', expecting '('

    ATi and Intel print using the following format::

        ERROR: 0:131: '{' : syntax error parse error
    """
    import re

    # Nvidia
    # 0(7): error C1008: undefined variable "MV"
    match = re.match( r'(\d+)\((\d+)\)\s*:\s(.*)', error )
    if match:
        return int(match.group(2)), match.group(3)
    
    # ATI / Intel
    # ERROR: 0:131: '{' : syntax error parse error
    match = re.match( r'ERROR:\s(\d+):(\d+):\s(.*)', error )
    if match:
        return int(match.group(2)), match.group( 3 )

    # Nouveau
    # 0:28(16): error: syntax error, unexpected ')', expecting '('
    match = re.match( r'(\d+):(\d+)\((\d+)\):\s(.*)', error )
    if match:
        return int(match.group(2)), match.group(4) 
    
    return None, error


def parse_shader_errors(errors, source=None):
    """Parses a GLSL error buffer and prints a list of
    errors, trying to show the line of code where the error 
    ocrrured.
    """
    # Init
    if not isinstance(errors, string_types):
        errors = errors.decode('utf-8', 'replace')
    results = []
    lines = None
    if source is not None:
        lines = [line.strip() for line in source.split('\n')]
    
    for error in errors.split('\n'):
        # Strip; skip empy lines
        error = error.strip()
        if not error:
            continue
        # Separate line number from description (if we can)
        linenr, error = parse_shader_error(error)
        if None in (linenr, lines):
            print('    %s' % error)
        else:
            print('    on line %i: %s' % (linenr, error))
            if linenr>0 and linenr < len(lines):
                print('        %s' % lines[linenr-1])

