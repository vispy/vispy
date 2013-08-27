# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Definition of shader program.

This code is inspired by similar classes from Pygly.

"""

from __future__ import print_function, division, absolute_import

import re
import sys
import weakref

import numpy as np

from vispy import gl
from . import GLObject, ext_available
from . import VertexBuffer, ElementBuffer
#from .program_inputs import UniformInputs, AttributeInputs
from .variable import Attribute, Uniform
from .shader import parse_shader_errors, VertexShader, FragmentShader
from vispy.util.six import string_types



class ProgramException(Exception):
    pass



class Program(GLObject):
    """ Representation of a shader program. It combines (links) a 
    vertex and a fragment shaders to compose a complete program.
    On (normal, non-ES 2.0) implementations, multiple shaders of 
    each type are allowed).
    
    Objects of this class are also used to set the uniforms and
    attributes that are used by the shaders. To do so, simply add
    attributes to the `uniforms` and `attributes` members. The names
    of the added attributes should match with those used in the shaders.
    
    Parameters
    ----------
    vert : Shader object or string
        The VertexShader for this program. The string can be a file name
        or the source of the shading code. It can also be a list of 
        shaders, but this is not supported on genuine OpenGL ES 2.0.
    frag : Shader object or string
        The FragmentShader for this program. The string can be a file name
        or the source of the shading code. It can also be a list of 
        shaders, but this is not supported on genuine OpenGL ES 2.0.
    
    """
    
    def __init__(self, vert=None, frag=None):
        GLObject.__init__(self)
        
        # Manage enabled state (i.e. activated)
        self._enabled = False
        self._enabled_objects = []
        
        # List of varying names to use for feedback
        self._feedback_vars = []
        
        # Inis lists of shaders
        self._verts = []
        self._frags = []
        
        # Containers for uniforms and attributes. 
        # name -> Variable
        self._attributes = {}
        self._uniforms = {}
        
        # Keep track of which names are active (queried after linking)
        # name -> location
        self._active_attributes = {}
        self._active_uniforms = {}
        
        # Keep track of number of vertices
        self._vertex_count = None
        
        shaders = []
        
        # Get all vertex shaders
        if vert is None:
            pass
        elif isinstance(vert, VertexShader):
            shaders.append(vert)
        elif isinstance(vert, string_types):
            shaders.append(VertexShader(vert))
        elif isinstance(vert, (list, tuple)):
            for shader in vert:
                if isinstance(shader, string_types):
                    shader = VertexShader(shader)
                shaders.append(shader)
        else:
            raise ValueError('Invalid value for VertexShader "%r"' % vert)
        
        # Get all fragment shaders
        if frag is None:
            pass
        elif isinstance(frag, FragmentShader):
            shaders.append(frag)
        elif isinstance(frag, string_types):
            shaders.append(FragmentShader(frag))
        elif isinstance(frag, (list, tuple)):
            for shader in frag:
                if isinstance(shader, string_types):
                    shader = FragmentShader(shader)
                shaders.append(shader)
        else:
            raise ValueError('Invalid value for FragmentShader "%r"' % frag)
        
        # Attach shaders now
        if shaders:
            self.attach(*shaders)
    
    
    def attach(self, *shaders):
        """ Attach one or more vertex/fragment shaders to the program. 
        
        Paramaters
        ----------
        *shaders : Shader objects
            The VertexShader or FragmentShader to attach.
        
        """
        # Tuple or list given?
        if len(shaders)==1 and isinstance(shaders[0], (list,tuple)):
            shaders = shaders[0]
        
        # Process each shader
        for shader in shaders:
            if isinstance(shader, VertexShader):
                self._verts.append(shader)
            elif isinstance(shader, FragmentShader):
                self._frags.append(shader)
            else:
                ValueError('Invalid value for shader "%r"' % shader)
        
        # Ensure uniqueness of shaders
        self._verts = list(set(self._verts))
        self._frags = list(set(self._frags))

        # Update dirty flag to induce a new build when necessary
        self._need_update = True

        # Build uniforms and attributes
        self._build_uniforms()
        self._build_attributes()

    
    def detach(self, *shaders):
        """ Detach one or several vertex/fragment shaders from the program.
        
        Paramaters
        ----------
        *shaders : Shader objects
            The VertexShader or FragmentShader to detach.
        
        """
        # Tuple or list given?
        if len(shaders)==1 and isinstance(shaders[0], (list,tuple)):
            shaders = shaders[0]
        
        # Process each shader
        for shader in shaders:
            if isinstance(shader, VertexShader):
                if shader in self._verts:
                    self._verts.remove(shader)
                else:
                    raise ShaderException("Shader is not attached to the program")
            elif isinstance(shader, FragmentShader):
                if shader in self._frags:
                    self._frags.remove(shader)
                else:
                    raise ShaderException("Shader is not attached to the program")
            else:
                ValueError('Invalid value for shader "%r"' % shader)
        
        # Update dirty flag to induce a new build when necessary
        self._need_update = True
        
        # Build uniforms and attributes
        self._build_uniforms()
        self._build_attributes()
    
    
    @property
    def shaders(self):
        """ List of shaders associated with this shading program.
        """
        return self._verts + self._frags
    
    
    def __setitem__(self, name, data):
        """ Behave a bit like a dict to assign attributes and uniforms.
        """
        assert isinstance(name, str)
        if name in self._uniforms.keys():
            # Auto-make Texture from numpy array, but warn if it replaces a previous
            texClass = self._uniforms[name]._textureClass
            if isinstance(data, np.ndarray) and texClass:
                data = texClass(data)
                if self._uniforms[name]._data is not None:
                    print("Warning: uniform '%s' is replaced with a new Texture. Better update the texture." % name)
            # Set data
            self._uniforms[name].set_data(data)
            # If program is currently in use, we upload immediately the data
            if self._enabled and name in self._active_uniforms:
               self._uniforms[name].upload(self)
            # Invalidate vertex count
            self._vertex_count = None
        elif name in self._attributes.keys():
            # Auto-make VBO from numpy array, but warn if it replaces a previous
            if isinstance(data, np.ndarray):
                data = VertexBuffer(data)
                if self._attributes[name]._data is not None:
                    print("Warning: attribute '%s' is replaced with a new VertexBuffer. Better update the VertexBuffer or use Program.set_var()." % name)
            # Set data
            self._attributes[name].set_data(data)
            # If program is currently in use, we upload immediately the data
            if self._enabled and name in self._active_attributes:
               self._attributes[name].upload(self)
        else:
            raise NameError("Unknown uniform or attribute: %s" % name)
    
    
    def set_var(self, *structured_vars, **keyword_vars):
        """ Set attribute data. This method accepts dictionary-like
        arguments (like numpy structured arrays), for which each element
        will be applied.
        
        Other than with ``Program['name'] = value``, a numpy array is
        not automatically converted to a VertexBuffer or Texture. Note
        that attributes can be numpy arrays, but this is generally
        discouraged.
        """
        D = {}
        
        # Process kwargs
        D.update(keyword_vars)
        
        # Process structured data
        for data in structured_vars:
            
            if isinstance(data, np.ndarray):
                # Structured array
                if data.dtype.fields:
                    print("Warning: attribute data given as a structured array, you probably want to use a VertexBuffer.")
                    for k in data.dtype.fields:
                        D[k] = data[k]
                else:
                    raise ValueError("Program.set_attr accepts a structured array, but normal arrays must be given as keyword args.")
            
            elif isinstance(data, VertexBuffer):
                # Vertex buffer
                if isinstance(data.type, dict):
                    for k in data.type:
                        D[k] = data[k]
                else:
                    raise ValueError('Can only set attributes with a structured VertexBuffer.')
            
            elif isinstance(data, dict):
                # Dict
                D.update(data)
            else:
                raise ValueError("Don't know how to use attribute of type %r" % type(data))
        
        # Apply each
        for name, data in D.items():
            #self[name] = data
            if name in self._uniforms.keys():
                self._uniforms[name].set_data(data)
                if self._enabled and name in self._active_uniforms:
                    self._uniforms[name].upload(self)
            elif name in self._attributes.keys():
                self._attributes[name].set_data(data)
                if self._enabled and name in self._active_attributes:
                    self._attributes[name].upload(self)
                # Invalidate vertex count
                self._vertex_count = None
            else:
                raise ValueError("Unknown uniform or attribute: %s" % name)
    
    
    @property
    def attributes(self):
        """ A list of all Attribute objects associated with this program
        (sorted by name).
        """
        return list( sorted(self._attributes.values(), key=lambda x:x.name ) )
    
    
    @property
    def uniforms(self):
        """ A list of all Uniform objects associated with this program
        (sorted by name).
        """
        return list( sorted(self._uniforms.values(), key=lambda x:x.name ) )
    
    
    def _get_vertex_count(self):
        """ Get count of the number of vertices.
        """
        if self._vertex_count is None:
            count = None
            for attribute in self.attributes:
                # Check if valid count 
                if attribute.count is None:
                    continue
                # Update count
                if count is None:
                    count = attribute.count
                elif attribute.count == count:
                    pass # OK
                elif attribute.count < count:
                    count = attribute.count
                    #print('Warning: attributes have unequal number of vertices.')
                else:
                    pass#print('Warning: attributes have unequal number of vertices.')
            self._vertex_count = count
        
        # Return
        return self._vertex_count
    
    
    def _build_attributes(self):
        """ Build the attribute objects 
        Called when shader is atatched/detached.
        """
        # Get all attributes (There are no attribute in fragment shaders)
        v_attributes, f_attributes = [], []
        for shader in self._verts:
            v_attributes.extend(shader._get_attributes())
        attributes = list(set(v_attributes + f_attributes))
        
        # Create Attribute objects for each one
        self._attributes = {}
        for (name, gtype) in attributes:
            attribute = Attribute(name, gtype)
            self._attributes[name] = attribute
    
    
    def _build_uniforms(self):
        """ Build the uniform objects 
        Called when shader is atatched/detached.
        """
        # Get al; uniformes
        v_uniforms, f_uniforms = [], []
        for shader in self._verts:
            v_uniforms.extend(shader._get_uniforms())
        for shader in self._frags:
            f_uniforms.extend(shader._get_uniforms())
        uniforms = list(set(v_uniforms + f_uniforms))
        
        # Create Uniform ojects for each one
        self._uniforms = {}
        for (name, gtype) in uniforms:
            uniform = Uniform(name, gtype)
            self._uniforms[name] = uniform
        
    
    def _mark_active_attributes(self):
        """ Mark which attributes are active and get the location.
        Called after linking. 
        """

        count = gl.glGetProgramiv(self.handle, gl.GL_ACTIVE_ATTRIBUTES)
        
        # This match a name of the form "name[size]" (= array)
        regex = re.compile("""(?P<name>\w+)\s*(\[(?P<size>\d+)\])""")
        
        # Find active attributes
        self._active_attributes = {}
        for i in range(count):
            name, size, gtype = gl.glGetActiveAttrib(self.handle, i)
            loc = gl.glGetAttribLocation(self._handle, name)
            name = name.decode('utf-8')
            # This checks if the attribute is an array
            # Name will be something like xxx[0] instead of xxx
            m = regex.match(name)
            # When attribute is an array, size corresponds to the highest used index
            if m:
                name = m.group('name')
                if size >= 1:
                    for i in range(size):
                        name = '%s[%d]' % (m.group('name'),i)
                        self._active_attributes[name] = loc
            else:
                self._active_attributes[name] = loc
        
        # Mark these as active (loc non-None means active)
        for attribute in self._attributes.values():
            attribute._loc = self._active_attributes.get(attribute.name, None)
    
    
    def _mark_active_uniforms(self):
        """ Mark which uniforms are actve, set the location, 
        for textures also set texture unit.
        Called after linking. 
        """

        count = gl.glGetProgramiv(self.handle, gl.GL_ACTIVE_UNIFORMS)
        
        # This match a name of the form "name[size]" (= array)
        regex = re.compile("""(?P<name>\w+)\s*(\[(?P<size>\d+)\])\s*""")
        
        # Find active uniforms
        self._active_uniforms = {}
        for i in range(count):
            name, size, gtype = gl.glGetActiveUniform(self.handle, i)
            loc = gl.glGetUniformLocation(self._handle, name)
            name = name.decode('utf-8')
            # This checks if the uniform is an array
            # Name will be something like xxx[0] instead of xxx
            m = regex.match(name)
            # When uniform is an array, size corresponds to the highest used index
            if m:
                name = m.group('name')
                if size >= 1:
                    for i in range(size):
                        name = '%s[%d]' % (m.group('name'),i)
                        self._active_uniforms[name] = loc
            else:
                self._active_uniforms[name] = loc
        
        # Mark these as active (loc non-None means active)
        texture_count = 0
        for uniform in self._uniforms.values():
            uniform._loc = self._active_uniforms.get(uniform.name, None)
            if uniform._loc is not None:
                if uniform._textureClass:
                    uniform._texture_unit = texture_count
                    texture_count += 1
    
    
    
    ## Behaver like a GLObject
    
    def _create(self):
        self._handle = gl.glCreateProgram()
    
    
    def _delete(self):
        gl.glDeleteProgram(self._handle)
    
    
    def _activate(self):
        # Use this program!
        gl.glUseProgram(self._handle)
        
        # Mark as enabled, prepare to enable other objects
        self._enabled = True
        self._enabled_objects = []
        
        # Upload any attributes and uniforms if necessary
        for variable in (self.attributes + self.uniforms):
            if variable.active:
                variable.upload(self)
    
    
    def _deactivate(self):
        for ob in reversed(self._enabled_objects):
            ob.deactivate()
        gl.glUseProgram(0)
        self._enabled = False
    
    
    def _update(self):
        
        # Check if we have something to link
        if not self._verts:
            raise ProgramException("No vertex shader has been given")
        if not self._frags:
            raise ProgramException("No fragment shader has been given")
        
        # Detach any attached shaders
        attached = gl.glGetAttachedShaders(self._handle)
        for handle in attached:
            gl.glDetachShader(self._handle, handle)
        
        # Attach and activate vertex and fragment shaders
        for shader in self.shaders:
            shader.activate()
            gl.glAttachShader(self._handle, shader.handle)
        
        # Only proceed if all shaders compiled ok
        oks = [shader._valid for shader in self.shaders]
        if not (oks and all(oks)):
            raise ProgramExceptionr('Shaders did not compile.')
        
        # Link the program
        # todo: should there be a try-except around this?
        gl.glLinkProgram(self._handle)
        if not gl.glGetProgramiv(self._handle, gl.GL_LINK_STATUS):
            errors = gl.glGetProgramInfoLog(self._handle)
            print(errors)
            #parse_shader_errors(errors)
            raise ProgramException('Linking error')
        
        # Mark all active attributes and uniforms
        self._mark_active_attributes()
        self._mark_active_uniforms()
    
    
    ## Drawing and enabling
    
    # todo: rename to activate_object, maybe make private
    def enable_object(self, object):
        """ Enable an object, e.g. a texture. The program
        will make sure that the object is disabled again.
        Can only be called while Program is active.
        """
        if not self._enabled:
            raise ProgramException("Program cannot enable an object if not self being enabled.")
        object.activate()
        self._enabled_objects.append(object)
    
    
    
    def draw_arrays(self, mode, first=0, count=None):
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
        
        # Prepare
        refcount = self._get_vertex_count()
        if count is None:
            count = refcount
        elif refcount:
            if count > refcount:
                raise ValueError('Count is larger than known number of vertices.')
        
        # Check if we know count
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
        
        # Prepare and draw
        if isinstance(indices, ElementBuffer):
            # Enable
            self.enable_object(indices)
            # Prepare
            offset = None  # todo: allow the use of offset
            gltype = ElementBuffer.DTYPES[indices.type]
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

