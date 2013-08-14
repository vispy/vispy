# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Definition of shader program.

This code is inspired by similar classes from Pygly.

"""

from __future__ import print_function, division, absolute_import

import sys
import weakref

import numpy as np

from vispy import gl
from . import GLObject, ext_available
from . import VertexBuffer, ElementBuffer
from .program_inputs import UniformInputs, AttributeInputs
from .shader import parse_shader_errors, VertexShader, FragmentShader


# todo: support uniform arrays of vectors/matrices?
# todo: more introspection into uniforms/attributes?

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
            self.attach_shader(shader)
        
        # Inputs
        self._uniform_inputs = UniformInputs(self)
        self._attribute_inputs = AttributeInputs(self)
        self._inputs = (self._uniform_inputs, self._attribute_inputs,)
        
        # List of names that we ask from OpenGL right after linking.
        self._uniform_names = []
        self._attribute_names = []
        
        # List of objects being enabled
        self._enabled_objects = []
        
        # List of varying names to use for feedback
        self._feedback_vars = []
    
    
    def _delete(self):
        gl.glDeleteProgram(self._handle)
    
    
    @property
    def uniforms(self):
        """ A dictionary for the uniform inputs to this shader program.
        For example: ``program.uniforms['u_color'] = 0.0, 1.0, 0.0``. 
        
        Uniforms can be a tuple/array of 1 to 4 elements to specify a
        vector, 4, 9 or 16 elements to specify a matrix, or a Texture
        object to specify a sampler.
        """
        return self._uniform_inputs
    
    
    @property
    def attributes(self):
        """ A dictionary for the attribute inputs to this shader program.
        For example: ``program.attributes['a_position'] = my_positions_array``. 
        
        Attributes can be a tuple of 1 to 4 elements (global attributes),
        a numpy array of per vertex attributes, or a VertexBuffer object
        (recommended over the numpy array).
        
        Note that one can use ``prog.attributes.update(my_stuctured_array)``
        or ``prog.attributes.update(my_stuctured_vbo)`` to map field names
        to attribute names automatically.
        """
        return self._attribute_inputs
    
    
    def attach_shader(self, shader):
        """ Attach the given vertex or fragment shader to this shader program.
        Multiple shaders can be attached (also e.g. multiple FragmentShaders).
        """
        if isinstance(shader, (VertexShader, FragmentShader)):
            self._shaders_to_add.append(shader)
            shader._on_attach(self)
        else:
            raise ValueError('attach_shader required VertexShader of FragmentShader.')
    
    
    def detach_shader(self, shader):
        """ Detach the given shader from this shader program. 
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
    
    
#     def get_vertex_shader(self, index=0):
#         """ Get the ith vertex shader for this shader program. Default first.
#         """
#         count = -1
#         for shader in self.shaders:
#             if isinstance(shader, VertexShader):
#                 count += 1
#                 if count == index:
#                     return shader
#         else:
#             return None
#     
# 
#     def get_fragment_shader(self, index=0):
#         """ Get the ith fragment shader for this shader program. Default first.
#         """
#         count = -1
#         for shader in self.shaders:
#             if isinstance(shader, FragmentShader):
#                 count += 1
#                 if count == index:
#                     return shader
#         else:
#             return None
    
    
    def _enable(self):
        if self._handle <= 0:# or not gl.glIsProgram(self._handle):
            self._handle = gl.glCreateProgram()
        
        # Remove/add shaders and compile them
        self._enable_shaders()
        
        # Only proceed if all shaders compiled ok
        oks = [shader._compiled==2 for shader in self._shaders]
        if not (oks and all(oks)):
            return
        
        #for s in self._shaders:
            #print(s._source)
        
        # enable transform feedback
        if len(self._feedback_vars) > 0:
            import ctypes
            arr = (ctypes.POINTER(ctypes.c_char)*len(self._feedback_vars))()
            for i,v in enumerate(self._feedback_vars):
                arr[i] = ctypes.create_string_buffer(v)
            gl.glTransformFeedbackVaryings(self.handle, len(self._feedback_vars), arr, gl.GL_INTERLEAVED_ATTRIBS)
        
        # Link the program?
        if not gl.glGetProgramiv(self.handle, gl.GL_LINK_STATUS):
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
            # Get list of uniforms and attributes, for diagnosis
            for input in self._inputs:
                input._on_linking()
        
        # Use this program!
        gl.glUseProgram(self._handle)
        
        # Mark as enabled, prepare to enable other objects
        self._enabled = True
        self._enabled_objects = []
        
        # Apply all uniforms, samplers and attributes
        for input in self._inputs:
            input._on_enabling()
            
        for shader in self._shaders:
            shader._on_enabling(self)
    
    
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
        for shader in self._shaders:
            shader._on_disabling()
    
    
    def draw_arrays(self, mode, first=None, count=None):
        """ Draw the attribute arrays in the specified mode.
        Only call when the program is enabled.
        
        Parameters
        ----------
        mode : GL_ENUM
            GL_POINTS, GL_LINES, GL_LINE_STRIP, GL_LINE_LOOP, 
            GL_TRIANGLES, GL_TRIANGLE_STRIP, GL_TRIANGLE_FAN
        first : int
            The starting vertex index in the vertex array. Default 0.
        count : int
            The number of vertices to draw. Default all.
        """
        # Check
        if not self._enabled:
            raise RuntimeError('draw_arrays require the ShaderProgram to be enabled.')
        for input in self._inputs: 
            input._on_drawing()
        
        # Prepare
        if first is None:
            first = 0
        if count is None:
            count = self.attributes.vertex_count
        if count is None:
            raise Exception("Could not determine element count for draw.")
        
        # Draw
        gl.glDrawArrays(mode, first, count)
    
    
    # todo: what does this do?
    def feedback_arrays(self, buf, mode, first=None, count=None):
        vbuf = VertexBuffer(data=buf)
        gl.glBindBufferBase(gl.GL_TRANSFORM_FEEDBACK_BUFFER, 0, vbuf._handle)
        fbmode = {
            gl.GL_POINTS: gl.GL_POINTS,
            gl.GL_LINES: gl.GL_LINES,
            gl.GL_LINE_STRIP: gl.GL_LINES,
            gl.GL_LINE_LOOP: gl.GL_LINES,
            gl.GL_TRIANGLES: gl.GL_TRIANGLES,
            gl.GL_TRIANGLE_STRIP: gl.GL_TRIANGLES,
            gl.GL_TRIANGLE_FAN: gl.GL_TRIANGLES,
            }[mode]
        gl.glBeginTransformFeedback(fbmode)
        try:
            self.draw_arrays(mode, first, count)
        finally:
            r = glEndTransformFeedback()
            print(r)
        return vbuf
    
    
    def draw_elements(self, mode, indices):
        """ Draw the attribute arrays using a specified set of vertices,
        in the specified mode.
        Only call when the program is enabled.
        
        Parameters
        ----------
        mode : GL_ENUM
            GL_POINTS, GL_LINES, GL_LINE_STRIP, GL_LINE_LOOP, 
            GL_TRIANGLES, GL_TRIANGLE_STRIP, GL_TRIANGLE_FAN
        indices : numpy_array or ElementBuffer
            The indices to the vertices in the vertex arrays to draw.
            For performance, ElementBuffer objects are recommended over
            numpy arrays. If an ElementBuffer is provided, this method
            takes care of enabling it.
        """
        # Check
        if not self._enabled:
            raise RuntimeError('draw_elements require the ShaderProgram to be enabled.')
        for input in self._inputs: 
            input._on_drawing()
     
        # Prepare and draw
        if isinstance(indices, ElementBuffer):
            # Enable
            self.enable_object(indices)
            # Prepare
            offset = None  # todo: allow the use of offset
            gltype = VertexBuffer.DTYPES[indices.type]
            # Draw
            gl.glDrawElements(mode, indices.count, gltype, offset) 
        
        elif isinstance(indices, np.ndarray):
            # Get type
            gltype = ElementBuffer.DTYPES.get(indices.dtype.name, None)
            if gltype is None:
                raise ValueError('Unsupported data type for ElementBuffer.')
            elif gltype == gl.GL_UNSIGNED_INT and not ext_available('element_index_uint'):
                raise ValueError('element_index_uint extension needed for uint32 ElementBuffer.')
            # Draw
            gl.glDrawElements(mode, indices.size, gltype, indices) 
            
        else:
            raise ValueError("draw_elements requires an ElementBuffer or a numpy array.")

