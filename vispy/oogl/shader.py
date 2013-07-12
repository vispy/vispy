# -*- coding: utf-8 -*-
""" Definition of classes related to shaders.

This code is inspired by similar classes from Pygly.

"""

from __future__ import print_function, division, absolute_import

import sys
import numpy as np

from vispy import gl
from . import GLObject, push_enable, pop_enable, ext_available


if sys.version_info > (3,):
    basestring = str



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
        self.set_source(source)
    
    
    # todo: move delete method to GLObject?
    def delete(self):
        """ Delete the shader from OpenGl memory.
        Note that the right context should be active when this method is 
        called.
        """
        try:
            if self._handle > 0:
                gl.glDeleteShader(self._handle)
        except Exception:
            pass
        self._handle = 0
    
    def __del__(self):
        self.delete()
    
    
    def set_source(self, source):
        """ Set the source of the shader.
        """
        self._source = source
        self._compiled = 0  # force recompile 
        # Try to get description from first line
        # EXPERIMENTAL
        self._desciption = self._source.split('\n',1)[0].strip(' \t/*')
    
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



class VertexShader(BaseShader):
    """ Representation of a vertex shader object.
    """
    def __init__(self, source=None):
        BaseShader.__init__(self, gl.GL_VERTEX_SHADER, source)
    
    def __repr__(self):
        if self._desciption:
            return "<VertexShader '%s'>" % self._desciption 
        else:
            return "<VertexShader at %s>" % hex(id(self)) 


class FragmentShader(BaseShader):
    """ Representation of a fragment shader object.
    """
    def __init__(self, source=None):
        BaseShader.__init__(self, gl.GL_FRAGMENT_SHADER, source)
    
    def __repr__(self):
        if self._desciption:
            return "<FragmentShader '%s'>" % self._desciption 
        else:
            return "<FragmentShader at %s>" % hex(id(self)) 


class ShaderProgram(GLObject):
    
    def __init__(self, *shaders):
        self._handle = 0
        self._shaders = []
        self._shaders_to_add = []
        self._shaders_to_remove = []
        for shader in shaders:
            self.add_shader(shader)
    
    
    def delete(self):
        """ Delete the shader program from OpenGl memory.
        Note that the right context should be active when this method is 
        called.
        """
        try:
            if self._handle > 0:
                gl.glDeleteProgram(self._handle)
        except Exception:
            pass
        self._handle = 0
    
    def __del__(self):
        self.delete()
    
    
    def add_shader(self, shader):
        """ Add the given vertex or fragment shader to this shader program.
        """
        if isinstance(shader, (VertexShader, FragmentShader)):
            self._shaders_to_add.append(shader)
        else:
            raise ValueError('add_shader required VertexShader of FragmentShader.')
    
    
    def remove_shader(self, shader):
        """ Remove the given shader from this shader program. 
        """
        if shader in self._shaders_to_add:
            self._shaders_to_add.remove(shader)
        if shader in self._shaders:
            if shader not in self._shaders_to_remove:
                self._shaders_to_remove.append(shader)    
    
    @property
    def shaders(self):
        """ List of shaders associated with this shading program.
        """
        # Compile list
        shaders = list(self._shaders)
        for shader in self._shaders_to_remove:
            while shader in shaders:
                shaders.remove(shader)
        for shader in self._shaders_to_add:
            shaders.append(shader)
        return shaders
    
    
    def get_vertex_shader(self, index=0):
        """ Get the ith vertex shader for this shader program. Default first.
        """
        count = -1
        for shader in self.shaders:
            if isinstance(shader, VertexShader):
                count += 1
                if count == index:
                    return shader
        else:
            return None
    

    def get_fragment_shader(self, index=0):
        """ Get the ith fragment shader for this shader program. Default first.
        """
        count = -1
        for shader in self.shaders:
            if isinstance(shader, FragmentShader):
                count += 1
                if count == index:
                    return shader
        else:
            return None
    
    
    def set_uniform(self, *arg):
        pass # Deal with lazy as well as direct mode.
    
    
    def set_attribute(self, *args):
        pass # vertex attributes. Deal with lazy as well as direct mode.
        
        
    def _enable(self):
        if self._handle <= 0:
            self._handle = gl.glCreateProgram()
        
        # Remove shaders
        while self._shaders_to_remove:
            shader = self._shaders_to_remove.pop(0)
            # Make OpenGL detach it
            if shader._handle > 0:
                try:
                    gl.glDetachShader(self._handle, shader._handle)
                except Exception:
                    pass
            # Remove from our list
            while shader in self._shaders:
                self._shaders.remove(shader)
        
        # Attach pending shaders
        while self._shaders_to_add:
            shader = self._shaders_to_add.pop(0)
            # Add to our list
            self._shaders.append(shader)
            # Make OpenGL attach it
            shader._enable()
            try:
                gl.glAttachShader(self._handle, shader._handle)
            except Exception as e:
                print("Error attaching shader %r" % shader)
                print("\tException: %s" % str(e))
                raise
        
        # Check/compile all shaders
        for shader in self._shaders:
            shader._enable()
        
        # Only proceed if all shaders compiled ok
        oks = [shader._compiled==2 for shader in self._shaders]
        if not (oks and all(oks)):
            return
        
        # Link the program
        try:
            gl.glLinkProgram(self._handle)
        except Exception as e:
            print( "Error linking shader:" )
            parse_shader_errors(e.description)
            raise

        # Retrieve the link status
        if not gl.glGetProgramiv(self.handle, gl.GL_LINK_STATUS):
            print( "Error linking shader:" )
            errors = gl.glGetProgramInfoLog(self._handle)
            parse_shader_errors(errors)
            raise RuntimeError(errors)
        
        # Use this program!
        gl.glUseProgram(self._handle)
    
    
    def _disable(self):
        gl.glUseProgram(0)
    


## Convenience funcsions used in this module

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
    if not isinstance(errors, basestring):
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
