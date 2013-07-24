# -*- coding: utf-8 -*-
""" Definition of shader program.

This code is inspired by similar classes from Pygly.

"""

from __future__ import print_function, division, absolute_import

import sys
import weakref

import numpy as np

from vispy import gl
from . import GLObject, push_enable, pop_enable, ext_available
from . import Texture, VertexShader, FragmentShader

if sys.version_info > (3,):
    basestring = str


# todo: support uniform arrays of vectors/matrices
# todo: use glGetActiveUniform to query all uniforms in use?


class ShaderProgram(GLObject):
    """ Representation of a shader program. It combines (links) one 
    or more vertex and fragment shaders to compose a complete program.
    Objects of this class are also used to set the uniforms and 
    attributes that are used by the shaders.
    
    """
    
    def __init__(self, *shaders):
        self._handle = 0
        # Shaders
        self._shaders = []
        self._shaders_to_add = []
        self._shaders_to_remove = []
        for shader in shaders:
            self.add_shader(shader)
        # Uniforms
        self._uniforms = {}
        self._uniforms_samplers = {}
        self._uniform_handles = {}
        # Attributes
        self._attribute_handles = {}
    
    
    def _delete(self):
        gl.glDeleteProgram(self._handle)
    
    
    # todo: Experimental use __setitem__ for uniforms
    def __setitem__(self, name, value):
        return self.set_uniform(name, value)
    
    
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
    
    
    def set_uniform(self, name, value):
        """ Set uniform value. The value can be a tuple of floats/ints,
        or a single numpy array. Uniform vectors can be 1,2,3,4 elements.
        Matrices can be 4, 9 or 16 elements. (To pass a 2x2 matrix, a
        2x2 numpy array should be given.)
        """
        
        if isinstance(value, float):
            value = np.array(value, np.float32)  # Make numpy array
        elif isinstance(value, int):
            value = np.array(value, np.int32)  # Make numpy array
        elif isinstance(value, (tuple, list)):
            # Make numpy array
            if isinstance(value[0], float):
                value = np.array(value, np.float32)
            else:
                value = np.array(value, np.int32)
        elif isinstance(value, np.ndarray):
            # Force float32 or int32
            if value.dtype == np.float32:
                pass
            elif value.dtype == np.float64:
                value = value.astype(np.float32)
            else:
                value = value.astype(np.int32)
        elif isinstance(value, Texture):
            # A Texture, i.e. sampler
            self._uniforms_samplers[name] = weakref.ref(value)
            return
        else:
            raise ValueError("Invalid attribute value.")
        
        # Check size 
        if value.size not in (1,2,3,4, 9, 16):
            raise ValueError("Invalid number of values for uniform")
        
        # Store
        self._uniforms[name] = value
    
    
    def _set_sampler(self, name, value):
        """ Used internally to set the uniform-sampler from a cached value.
        """
        
        # Get value from weakref
        value = value()
        if value is None:
            return
        
        # Get uniform location
        try:
            loc = self._uniform_handles[name]
        except KeyError:
            loc = gl.glGetUniformLocation(self.handle, name.encode('utf-8'))
            self._uniform_handles[name] = loc
        
        # Our uniform may have been optimized out
        if loc < 0:
            return 
        
        # Apply 
        # NOTE: we are using a private attribute of Texture here ...
        gl.glUniform1i(loc, value._unit)
    
    
    def _set_uniform(self, name, value):
        """ Used internally to set the uniform from a cached value.
        """
        
        # Get uniform location
        try:
            loc = self._uniform_handles[name]
        except KeyError:
            loc = gl.glGetUniformLocation(self.handle, name.encode('utf-8'))
            self._uniform_handles[name] = loc
        
        # Our uniform may have been optimized out
        if loc < 0:
            return 
        
        # Get properties
        count = value.size
        isfloat = value.dtype == np.float32
        transpose = False
        ismatrix = False
        if count > 4 or value.shape == (2,2):
            ismatrix = True
            if not isfloat:
                value = value.astype(np.float32)
        
        # Apply
        if ismatrix:
            try:
                {   4 : gl.glUniformMatrix2fv,
                    9 : gl.glUniformMatrix3fv,
                    16 : gl.glUniformMatrix4fv}[count](loc, 1, transpose, value)
            except KeyError:
                raise RuntimeError("Unknown uniform matrix format")
        elif isfloat:
            try:
                {   1 : gl.glUniform1fv,
                    2 : gl.glUniform2fv,
                    3 : gl.glUniform3fv,
                    4 : gl.glUniform4fv}[count](loc, 1, value)
            except KeyError:
                raise RuntimeError("Unknown uniform float format")
        else:
            try:
                {   1 : gl.glUniform1iv,
                    2 : gl.glUniform2iv,
                    3 : gl.glUniform3iv,
                    4 : gl.glUniform4iv}[count](loc, 1, value)
            except KeyError:
                raise RuntimeError("Unknown uniform int format")
    
    
    def set_attribute(self, name, index):
        self._attributes[name, index]
        
        #gl.glGetAttribLocation(self._handle, name)
        #gl.glBindAttribLocation(self._handle, index, name)
        
    
    def get_attribute_location(self, name):
        """ Only use when "enabled".
        """
        # Try cached
        try:
            return self._attribute_handles[name]
        except KeyError:
            pass
        # Ask opengl for the location
        loc = gl.glGetAttribLocation(self._handle, name.encode('utf-8'))
        self._attribute_handles[name] = loc
        return loc
    
    #def _set_attribute(self, name, index):
        
        
        
        
    def _enable(self):
        if self._handle <= 0:# or not gl.glIsProgram(self._handle):
            self._handle = gl.glCreateProgram()
        
        # Remove/add shaders and compile them
        self._enable_shaders()
        
        # Only proceed if all shaders compiled ok
        oks = [shader._compiled==2 for shader in self._shaders]
        if not (oks and all(oks)):
            return
        
        # Link the program?
        if not gl.glGetProgramiv(self.handle, gl.GL_LINK_STATUS):
            # Force re-locating uniforms
            self._uniform_handles = {}  
            # Link!
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
        
        # Apply all uniforms
        for name, value in self._uniforms.items():
            self._set_uniform(name, value)
        for name, value in self._uniforms_samplers.items():
            self._set_sampler(name, value)
    
    
    def _enable_shaders(self):
        
        # Remove shaders if we must
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
