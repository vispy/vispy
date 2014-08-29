# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import re
import numpy as np

from . import gl
from .globject import GLObject
from .buffer import VertexBuffer, IndexBuffer
from .shader import VertexShader, FragmentShader
from .texture import GL_SAMPLER_3D
from .variable import Uniform, Attribute
from .wrappers import _check_conversion
from ..util import logger


_known_draw_modes = dict()
for key in ('points', 'lines', 'line_strip', 'line_loop',
            'triangles', 'triangle_strip', 'triangle_fan'):
    x = getattr(gl, 'GL_' + key.upper())
    _known_draw_modes[key] = x
    _known_draw_modes[x] = x  # for speed in this case


# ----------------------------------------------------------- Program class ---
class Program(GLObject):
    """ Shader program object

    A Program is an object to which shaders can be attached and linked to
    create the final program.

    Parameters
    ----------
    vert : str, VertexShader, or list
        The vertex shader to be used by this program
    frag : str, FragmentShader, or list
        The fragment shader to be used by this program
    count : int (optional)
        Number of vertices this program will use. This can be given to
        initialize a VertexBuffer during Program initialization.

    Notes
    -----
    If several shaders are specified, only one can contain the main
    function. OpenGL ES 2.0 does not support a list of shaders.
    """

    # ---------------------------------
    def __init__(self, vert=None, frag=None, count=0):
        GLObject.__init__(self)

        self._count = count
        self._buffer = None
        
        self._need_build = True
        
        # Init uniforms and attributes
        self._uniforms = {}
        self._attributes = {}
        
        # Get all vertex shaders
        self._verts = []
        if isinstance(vert, (str, VertexShader)):
            verts = [vert]
        elif isinstance(vert, (type(None), tuple, list)):
            verts = vert or []
        else:
            raise ValueError('Vert must be str, VertexShader or list')
        # Apply
        for shader in verts:
            if isinstance(shader, str):
                self._verts.append(VertexShader(shader))
            elif isinstance(shader, VertexShader):
                if shader not in self._verts:
                    self._verts.append(shader)
            else:
                T = type(shader)
                raise ValueError('Cannot make a VertexShader of %r.' % T)

        # Get all fragment shaders
        self._frags = []
        if isinstance(frag, (str, FragmentShader)):
            frags = [frag]
        elif isinstance(frag, (type(None), tuple, list)):
            frags = frag or []
        else:
            raise ValueError('Frag must be str, FragmentShader or list')
        # Apply
        for shader in frags:
            if isinstance(shader, str):
                self._frags.append(FragmentShader(shader))
            elif isinstance(shader, FragmentShader):
                if shader not in self._frags:
                    self._frags.append(shader)
            else:
                T = type(shader)
                raise ValueError('Cannot make a FragmentShader of %r.' % T)

        # Build uniforms and attributes
        self._create_variables()

        # Build associated structured vertex buffer if count is given
        if self._count > 0:
            dtype = []
            for attribute in self._attributes.values():
                dtype.append(attribute.dtype)
            self._buffer = VertexBuffer(np.zeros(self._count, dtype=dtype))
            self.bind(self._buffer)

    def attach(self, shaders):
        """ Attach one or several vertex/fragment shaders to the program
        
        Note that GL ES 2.0 only supports one vertex and one fragment 
        shader.
        
        Parameters
        ----------
        
        shaders : list of shade objects
            The shaders to attach.
        """

        if isinstance(shaders, (VertexShader, FragmentShader)):
            shaders = [shaders]
        for shader in shaders:
            if isinstance(shader, VertexShader):
                self._verts.append(shader)
            else:
                self._frags.append(shader)

        # Ensure uniqueness of shaders
        self._verts = list(set(self._verts))
        self._frags = list(set(self._frags))

        self._need_create = True
        self._need_build = True

        # Build uniforms and attributes
        self._create_variables()

    def detach(self, shaders):
        """Detach one or several vertex/fragment shaders from the program.
    
        Parameters
        ----------
        shaders : list of shade objects
            The shaders to detach.
        
        Notes
        -----
        We don't need to defer attach/detach shaders since shader deletion
        takes care of that.
        """

        if isinstance(shaders, (VertexShader, FragmentShader)):
            shaders = [shaders]
        for shader in shaders:
            if isinstance(shader, VertexShader):
                if shader in self._verts:
                    self._verts.remove(shader)
                else:
                    raise RuntimeError("Shader is not attached to the program")
            if isinstance(shader, FragmentShader):
                if shader in self._frags:
                    self._frags.remove(shader)
                else:
                    raise RuntimeError("Shader is not attached to the program")
        self._need_build = True

        # Build uniforms and attributes
        self._create_variables()

    def _create(self):
        """
        Create the GL program object if needed.
        """
        # Check if program has been created
        if self._handle <= 0:
            self._handle = gl.glCreateProgram()
            if not self._handle:
                raise RuntimeError("Cannot create program object")
    
    def _delete(self):
        logger.debug("GPU: Deleting program")
        gl.glDeleteProgram(self._handle)
    
    def _activate(self):
        """Activate the program as part of current rendering state."""
        
        #logger.debug("GPU: Activating program")
        
        # Check whether we need to rebuild shaders and create variables
        if any(s._need_compile for s in self.shaders):
            self._need_build = True
        
        # Stuff we need to do *before* glUse-ing the program
        did_build = False
        if self._need_build:
            did_build = True
            self._build()
            self._need_build = False
        
        # Go and use the prrogram
        gl.glUseProgram(self.handle)
        
        # Stuff we need to do *after* glUse-ing the program
        self._activate_variables()
        
        # Validate. We need to validate after textures units get assigned
        # (glUniform1i() gets called in _update() in variable.py)
        if did_build:
            gl.glValidateProgram(self._handle)
            if not gl.glGetProgramParameter(self._handle, 
                                            gl.GL_VALIDATE_STATUS):
                print(gl.glGetProgramInfoLog(self._handle))
                raise RuntimeError('Program validation error')
    
    def _deactivate(self):
        """Deactivate the program."""

        logger.debug("GPU: Deactivating program")
        gl.glUseProgram(0)
        self._deactivate_variables()
    
    def _build(self):
        """
        Build (link) the program and checks everything's ok.

        A GL context must be available to be able to build (link)
        """
        # Check if we have something to link
        if not self._verts:
            raise ValueError("No vertex shader has been given")
        if not self._frags:
            raise ValueError("No fragment shader has been given")

        # Detach any attached shaders
        attached = gl.glGetAttachedShaders(self._handle)
        for handle in attached:
            gl.glDetachShader(self._handle, handle)

        # Attach vertex and fragment shaders
        for shader in self._verts:
            shader.activate()
            gl.glAttachShader(self._handle, shader.handle)
        for shader in self._frags:
            shader.activate()
            gl.glAttachShader(self._handle, shader.handle)

        logger.debug("GPU: Creating program")

        # Link the program
        gl.glLinkProgram(self._handle)
        if not gl.glGetProgramParameter(self._handle, gl.GL_LINK_STATUS):
            print(gl.glGetProgramInfoLog(self._handle))
            raise RuntimeError('Program linking error')
        
        # Now we know what variable will be used by the program
        self._enable_variables()
    
    def _create_variables(self):
        """ Create the uniform and attribute objects based on the
        provided GLSL. This method is called when the GLSL is changed.
        """
        
        # todo: maybe we want to restore previously set variables, 
        # so that uniforms and attributes do not have to be set each time
        # that the shaders are updated. However, we should take into account
        # that typically all shaders are removed (i.e. no variables are
        # present) and then the new shaders are added.

        # Build uniforms
        self._uniforms = {}
        count = 0
        for (name, gtype) in self.all_uniforms:
            uniform = Uniform(self, name, gtype)
            # if gtype in (gl.GL_SAMPLER_1D, gl.GL_SAMPLER_2D):
            if gtype in (gl.GL_SAMPLER_2D, GL_SAMPLER_3D):
                uniform._unit = count
                count += 1
            self._uniforms[name] = uniform
        
        # Build attributes
        self._attributes = {}
        dtype = []
        for (name, gtype) in self.all_attributes:
            attribute = Attribute(self, name, gtype)
            self._attributes[name] = attribute
            dtype.append(attribute.dtype)
    
    def _enable_variables(self):  # previously _update
        """ Enable the uniform and attribute objects that will actually be
        used by the Program. i.e. variables that are optimised out are
        disabled. This method is called after the program has been buid.
        """
        # Enable uniforms
        active_uniforms = [name for (name, gtype) in self.active_uniforms]
        for uniform in self._uniforms.values():
            uniform.enabled = uniform.name in active_uniforms
        # Enable attributes
        active_attributes = [name for (name, gtype) in self.active_attributes]
        for attribute in self._attributes.values():
            attribute.enabled = attribute.name in active_attributes
    
    def _activate_variables(self):
        """ Activate the uniforms and attributes so that the Program
        can use them. This method is called when the Program gets activated.
        """
        for uniform in self._uniforms.values():
            if uniform.enabled:
                uniform.activate()
        for attribute in self._attributes.values():
            if attribute.enabled:
                attribute.activate()

    def _deactivate_variables(self):
        """ Deactivate all enabled uniforms and attributes. This method
        gets called when the Program gets deactivated.
        """
        for uniform in self._uniforms.values():
            if uniform.enabled:
                uniform.deactivate()
        for attribute in self._attributes.values():
            if attribute.enabled:
                attribute.deactivate()
    
    def bind(self, data):
        """ Bind a VertexBuffer that has structured data
        
        Parameters
        ----------
        data : VertexBuffer
            The vertex buffer to bind. The field names of the array
            are mapped to attribute names in GLSL.
        """
        # Check
        if not isinstance(data, VertexBuffer):
            raise ValueError('Program.bind() requires a VertexBuffer.')
        # Apply
        for name in data.dtype.names:
            if name in self._attributes.keys():
                self._attributes[name].set_data(data[name])
            else:
                logger.warning("%s has not been bound" % name)

    def __setitem__(self, name, data):
        try:
            if name in self._uniforms.keys():
                self._uniforms[name].set_data(data)
            elif name in self._attributes.keys():
                self._attributes[name].set_data(data)
            else:
                raise KeyError("Unknown uniform or attribute %s" % name)
        except Exception:
            logger.error("Could not set variable '%s' with value %s" % 
                         (name, data))
            raise

    def __getitem__(self, name):
        if name in self._uniforms.keys():
            return self._uniforms[name].data
        elif name in self._attributes.keys():
            return self._attributes[name].data
        else:
            raise KeyError("Unknown uniform or attribute %s" % name)

    @property
    def all_uniforms(self):
        """ Program uniforms obtained from shaders code """

        uniforms = []
        for shader in self._verts:
            uniforms.extend(shader.uniforms)
        for shader in self._frags:
            uniforms.extend(shader.uniforms)
        uniforms = list(set(uniforms))
        return uniforms

    @property
    def active_uniforms(self):
        """ Program active uniforms obtained from GPU """

        count = gl.glGetProgramParameter(self.handle, gl.GL_ACTIVE_UNIFORMS)
        # This match a name of the form "name[size]" (= array)
        regex = re.compile("""(?P<name>\w+)\s*(\[(?P<size>\d+)\])\s*""")
        uniforms = []
        for i in range(count):
            name, size, gtype = gl.glGetActiveUniform(self.handle, i)
            # This checks if the uniform is an array
            # Name will be something like xxx[0] instead of xxx
            m = regex.match(name)
            # When uniform is an array, size corresponds to the highest used
            # index
            if m:
                name = m.group('name')
                if size >= 1:
                    for i in range(size):
                        name = '%s[%d]' % (m.group('name'), i)
                        uniforms.append((name, gtype))
            else:
                uniforms.append((name, gtype))

        return uniforms

    @property
    def inactive_uniforms(self):
        """ Program inactive uniforms obtained from GPU """

        active_uniforms = self.active_uniforms
        inactive_uniforms = self.all_uniforms
        for uniform in active_uniforms:
            if uniform in inactive_uniforms:
                inactive_uniforms.remove(uniform)
        return inactive_uniforms

    @property
    def all_attributes(self):
        """ Program attributes obtained from shaders code """

        attributes = []
        for shader in self._verts:
            attributes.extend(shader.attributes)
        # No attribute in fragment shaders
        attributes = list(set(attributes))
        return attributes

    @property
    def active_attributes(self):
        """ Program active attributes obtained from GPU """

        count = gl.glGetProgramParameter(self.handle, gl.GL_ACTIVE_ATTRIBUTES)
        attributes = []

        # This match a name of the form "name[size]" (= array)
        regex = re.compile("""(?P<name>\w+)\s*(\[(?P<size>\d+)\])""")

        for i in range(count):
            name, size, gtype = gl.glGetActiveAttrib(self.handle, i)

            # This checks if the attribute is an array
            # Name will be something like xxx[0] instead of xxx
            m = regex.match(name)
            # When attribute is an array, size corresponds to the highest used
            # index
            if m:
                name = m.group('name')
                if size >= 1:
                    for i in range(size):
                        name = '%s[%d]' % (m.group('name'), i)
                        attributes.append((name, gtype))
            else:
                attributes.append((name, gtype))
        return attributes

    @property
    def inactive_attributes(self):
        """ Program inactive attributes obtained from GPU """

        active_attributes = self.active_attributes
        inactive_attributes = self.all_attributes
        for attribute in active_attributes:
            if attribute in inactive_attributes:
                inactive_attributes.remove(attribute)
        return inactive_attributes

    @property
    def shaders(self):
        """ List of shaders currently attached to this program """

        shaders = []
        shaders.extend(self._verts)
        shaders.extend(self._frags)
        return shaders

    def draw(self, mode=gl.GL_TRIANGLES, indices=None, check_error=True):
        """ Draw the attribute arrays in the specified mode.

        Parameters
        ----------
        mode : str | GL_ENUM
            GL_POINTS, GL_LINES, GL_LINE_STRIP, GL_LINE_LOOP,
            GL_TRIANGLES, GL_TRIANGLE_STRIP, GL_TRIANGLE_FAN
        indices : array
            Array of indices to draw.
        check_error:
            Check error after draw.
        """
        mode = _check_conversion(mode, _known_draw_modes)
        self.activate()
        if check_error:  # need to do this after activating, too
            gl.check_error('Check after draw activation')

        # WARNING: The "list" of values from a dict is not a list (py3k)
        attributes = list(self._attributes.values())
        sizes = [a.size for a in attributes]
        if len(attributes) < 1:
            raise RuntimeError('Must have at least one attribute')
        if not all(s == sizes[0] for s in sizes[1:]):
            msg = '\n'.join(['%s: %s' % (str(a), a.size) for a in attributes])
            raise RuntimeError('All attributes must have the same size, got:\n'
                               '%s' % msg)

        if isinstance(indices, IndexBuffer):
            indices.activate()
            logger.debug("Program drawing %d %r (using index buffer)", 
                         indices.size, mode)
            gltypes = {np.dtype(np.uint8): gl.GL_UNSIGNED_BYTE,
                       np.dtype(np.uint16): gl.GL_UNSIGNED_SHORT,
                       np.dtype(np.uint32): gl.GL_UNSIGNED_INT}
            gl.glDrawElements(mode, indices.size, gltypes[indices.dtype], None)
            indices.deactivate()
        elif indices is None:
            #count = (count or attributes[0].size) - first
            first = 0
            count = attributes[0].size
            logger.debug("Program drawing %d %r (no index buffer)", 
                         count, mode)
            gl.glDrawArrays(mode, first, count)
        else:
            raise TypeError("Invalid index: %r (must be IndexBuffer)" %
                            indices)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        self.deactivate()

        # Check ok
        if check_error:
            gl.check_error('Check after drawing completes')
