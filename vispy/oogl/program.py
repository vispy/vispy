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
from . import VertexShader, FragmentShader
from .program_inputs import UniformInputs, AttributeInputs

 
if sys.version_info > (3,):
    basestring = str


# todo: support uniform arrays of vectors/matrices
# todo: use glGetActiveUniform to query all uniforms in use?
# todo: allow setting of uniforms and attributes on the program object? u_color, a_pos


class ShaderProgram(GLObject):
    """ Representation of a shader program. It combines (links) one 
    or more vertex and fragment shaders to compose a complete program.
    
    Objects of this class are also used to set the uniforms and
    attributes that are used by the shaders. To do so, simply add
    attributes to the `uniforms` and `attributes` members. The names
    of the added attributes should match with those used in the shaders.
    """
    
    def __init__(self, *shaders):
        self._handle = 0
        self._enabled = False
        # Shaders
        self._shaders = []
        self._shaders_to_add = []
        self._shaders_to_remove = []
        for shader in shaders:
            self.add_shader(shader)
        
        # Inputs
        self._uniform_inputs = UniformInputs(self)
        self._attribute_inputs = AttributeInputs(self)
        self._inputs = (self._uniform_inputs, self._attribute_inputs,)
        
        # List of objects being enabled
        self._enabled_objects = []
    
    
    def _delete(self):
        gl.glDeleteProgram(self._handle)
    
    
    @property
    def uniforms(self):
        """ A namespace for the uniform inputs to this shader program.
        For example: ``program.uniforms.color = 0.0, 1.0, 0.0``. 
        
        Uniforms can be a tuple/array of 1 to 4 elements to specify a vector,
        a numpy array of 4, 9 or 16 elements to specify a matrix, or
        a Texture object to specify a sampler.
        """
        return self._uniform_inputs
    
    
    @property
    def attributes(self):
        """ A namespace for the attribute inputs to this shader program.
        For example: ``program.attributes.positions = my_positions_array``. 
        
        Attributes can be a tuple of 1 to 4 elements (global attributes),
        a numpy array of per vertex attributes, or a VertexBuffer object
        (recommended over the numpy array).
        """
        return self._attribute_inputs
    
    
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
            for input in self._inputs:
                input._clear_cache()
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
        
        # Mark as enabled, prepare to enable other objects
        self._enabled = True
        self._enabled_objects = []
        
        # Apply all uniforms, samplers and attributes
        for input in self._inputs:
            input._apply_static()
    
    
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
    
    
    def enable_object(self, object):
        """ Enable an object, e.g. a texture. The program
        will make sure that the object is disabled again.
        Can only be called while being used in a context.
        """
        if not self._enabled:
            raise RuntimeError("Program cannot enable an object if not self being enabled.")
        object._enable()
        self._enabled_objects.append(object)
    
    
    def _disable(self):
        for ob in reversed(self._enabled_objects):
            ob._disable()
        gl.glUseProgram(0)
        self._enabled = False
    


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
