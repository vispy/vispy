# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Definition of shader classes.

This code is inspired by similar classes from Pygly.

"""

from __future__ import print_function, division, absolute_import

import sys

import numpy as np

from vispy import gl
from vispy.util.six import string_types
from . import GLObject, ext_available



class BaseShader(GLObject):
    """ Abstract shader class.
    """
    
    def __init__(self, type, source=None):
        
        # Check and store type
        if type not in [gl.GL_VERTEX_SHADER, gl.GL_FRAGMENT_SHADER]:
            raise ValueError('Type must be vertex or fragment shader.')
        self._type = type
        
        self._handle = 0
        self._compiled = 0  # 0: not compiled, 1: compile tried, 2: compile success 
        self._description = None
        self._program = None  # pointer to the *currently enabled* program that includes this shader
        self.set_source(source)
    
    
    def _delete(self):
        gl.glDeleteShader(self._handle)
    
    
    def set_source(self, source):
        """ Set the source of the shader.
        """
        if not (isinstance(source, string_types) or source is None):
            raise TypeError('source argument must be string or None (%s)' % type(source))
        self._source = source
        self._compiled = 0  # force recompile 
        self._description = None
    
    
    def add_source(self, source):
        """ Templating, for later.
        """
        raise NotImplemented()
    
    
    def _enable(self):
        
        if self._handle <= 0:
            self._handle = gl.glCreateShader(self._type)
        
        # todo: what should happen if no source is given?
        if not self._source:
            self._compiled = 2
            return
        
        # If shader is compiled, we're done now
        if self._compiled:
            return 
        
        # Set compiled flag. It means that we tried to compile
        self._compiled = 1
        
        # Set source
        gl.glShaderSource(self._handle, self._source)
        
        # Compile the shader
        try:
            gl.glCompileShader(self._handle)
        except Exception as e:
            print( "Error compiling shader %r" % self )
            parse_shader_errors(e.description, self._source)
            raise

        # retrieve the compile status
        if not gl.glGetShaderiv(self._handle, gl.GL_COMPILE_STATUS):
            print( "Error compiling shader %r" % self )
            errors = gl.glGetShaderInfoLog(self._handle)
            parse_shader_errors(errors, self._source)
            raise RuntimeError(errors)
        
        # If we get here, compile is succesful
        self._compiled = 2
    
    
    def _disable(self):
        pass

    def __repr__(self):
        if self._description is None:
            # Try to get description from beginning of source
            if self._source is None:
                self._description = hex(id(self))
            else:
                for line in self._source.split('\n'):
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
    
    def _on_enabling(self, program):
        self._program = program

    def _on_disabling(self):
        self._program = None

    def _on_attach(self, program):
        pass

class VertexShader(BaseShader):
    """ Representation of a vertex shader object. Inherits BaseShader.
    """
    def __init__(self, source=None):
        BaseShader.__init__(self, gl.GL_VERTEX_SHADER, source)



class FragmentShader(BaseShader):
    """ Representation of a fragment shader object. Inherits BaseShader.
    """
    def __init__(self, source=None):
        BaseShader.__init__(self, gl.GL_FRAGMENT_SHADER, source)



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
        return (
            int(match.group( 2 )),   # line number
            match.group( 3 )    # description
            )

    # ATI
    # Intel
    # ERROR: 0:131: '{' : syntax error parse error
    match = re.match( r'ERROR:\s(\d+):(\d+):\s(.*)', error )
    if match:
        return (
            int(match.group( 2 )),   # line number
            match.group( 3 )    # description
            )

    # Nouveau
    # 0:28(16): error: syntax error, unexpected ')', expecting '('
    match = re.match( r'(\d+):(\d+)\((\d+)\):\s(.*)', error )
    if match:
        return (
            int(match.group( 2 )),   # line number
            match.group( 4 )    # description
            )
    
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

