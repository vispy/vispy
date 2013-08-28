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



class ProgramError(RuntimeError):
    """ Raised when something goes wrong that depens on state that was set 
    earlier (due to deferred loading).
    """
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
        self._active = False
        self._activated_objects = []
        
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
        This is the preferred way for the user to set uniforms and attributes.
        """
        if name in self._uniforms.keys():
            # Set data and invalidate vertex count
            self._uniforms[name].set_data(data)
            self._vertex_count = None
        elif name in self._attributes.keys():
            # Set data
            self._attributes[name].set_data(data)
        else:
            raise NameError("Unknown uniform or attribute: %s" % name)
    
    
    def set_vars(self, vars=None, **keyword_vars):
        """ Set variables from a dict-like object. vars can be a dict
        or a structured numpy array. This is a convenience function
        that is more or less equivalent to:
        ``for name in vars: program[name] = vars[name]``
        
        """
        D = {}
        
        # Process kwargs
        D.update(keyword_vars)
        
        # Process vars
        if vars is None:
            pass
        elif isinstance(vars, np.ndarray):
            # Structured array
            if vars.dtype.fields:
                print("Warning: attribute data given as a structured " +
                        "array, you probably want to use a VertexBuffer.")
                for k in vars.dtype.fields:
                    D[k] = vars[k]
            else:
                raise ValueError("Program.set_attr accepts a structured " +
                    "array, but normal arrays must be given as keyword args.")
        
        elif isinstance(vars, VertexBuffer):
            # Vertex buffer
            if isinstance(vars.type, dict):
                for k in vars.type:
                    D[k] = vars[k]
            else:
                raise ValueError('Can only set attributes with a ' + 
                                    'structured VertexBuffer.')
        
        elif isinstance(vars, dict):
            # Dict
            D.update(vars)
        else:
            raise ValueError("Don't know how to use attribute of type %r" %
                                        type(vars))
        
        # Apply each
        for name, data in D.items():
            self[name] = data
    
    
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
        The count will only be recalculated if necessary, so if the
        attributes have not changed, this function call should be quick.
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
                else:
                    #if count != attribute.count:
                    #    print('Warning: attributes have unequal number of vertices.')
                    count = min(count, attribute.count)
            self._vertex_count = count
        
        # Return
        return self._vertex_count
    
    
    def _build_attributes(self):
        """ Build the attribute objects.
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
        """ Build the uniform objects. 
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
        """ Mark which attributes are active and set the location.
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
        """ Mark which uniforms are actve and set the location, 
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
        """
          * Activate ourselves
          * Prepare for activating other objects.
          * Upload pending variables.
        """
        
        # Use this program!
        gl.glUseProgram(self._handle)
        
        # Mark as enabled, prepare to enable other objects
        self._active = True
        self._activated_objects = []
    
    
    def _deactivate(self):
        """ Deactivate any objects that were activated on our behalf,
        and then deactivate ourself.
        """
        for ob in reversed(self._activated_objects):
            ob.deactivate()
        gl.glUseProgram(0)
        self._active = False
    
    
    def _update(self):
        """ Called when the object is activated and the _need_update
        flag is set
        """
        
        # Check if we have something to link
        if not self._verts:
            raise ProgramError("No vertex shader has been given")
        if not self._frags:
            raise ProgramError("No fragment shader has been given")
        
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
            raise ProgramErrorr('Shaders did not compile.')
        
        # Link the program
        # todo: should there be a try-except around this?
        gl.glLinkProgram(self._handle)
        if not gl.glGetProgramiv(self._handle, gl.GL_LINK_STATUS):
            errors = gl.glGetProgramInfoLog(self._handle)
            print(errors)
            #parse_shader_errors(errors)
            raise ProgramError('Linking error')
        
        # Mark all active attributes and uniforms
        self._mark_active_attributes()
        self._mark_active_uniforms()
    
    
    ## Drawing and enabling
    
    
    def activate_object(self, object):
        """ Activate an object, e.g. a texture. The program
        will make sure that the object is disabled again.
        Can only be called while Program is active.
        """
        if not self._active:
            raise ProgramError("Program cannot enable an object if not self being enabled.")
        object.activate()
        self._activated_objects.append(object)
    
    
    
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
        if not self._active:
            raise ProgramError('ShaderProgram must be active when drawing.')
        
        # Upload any attributes and uniforms if necessary
        for variable in (self.attributes + self.uniforms):
            if variable.active:
                variable.upload(self)
        
        # Prepare
        refcount = self._get_vertex_count()
        if count is None:
            count = refcount
        elif refcount:
            if count > refcount:
                raise ValueError('Count is larger than known number of vertices.')
        
        # Check if we know count
        if count is None:
            raise ProgramError("Could not determine element count for draw.")
        
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
        if not self._active:
            raise ProgramError('Program must be active for drawing.')
        
        # Upload any attributes and uniforms if necessary
        for variable in (self.attributes + self.uniforms):
            if variable.active:
                variable.upload(self)
        
        # Prepare and draw
        if isinstance(indices, ElementBuffer):
            # Activate
            self.activate_object(indices)
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

