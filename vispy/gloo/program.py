# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Definition of shader program.

This code is inspired by similar classes from Pygly.

"""

from __future__ import division

import re

import numpy as np

from . import gl
from . import GLObject, ext_available, convert_to_enum
from . import VertexBuffer, ElementBuffer
from .buffer import ClientElementBuffer
from .variable import Attribute, Uniform
from .shader import VertexShader, FragmentShader, ShaderError
from ..util import is_string, logger


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
        elif is_string(vert):
            shaders.append(VertexShader(vert))
        elif isinstance(vert, (list, tuple)):
            for shader in vert:
                if is_string(shader):
                    shader = VertexShader(shader)
                shaders.append(shader)
        else:
            raise ValueError('Invalid value for VertexShader "%r"' % vert)

        # Get all fragment shaders
        if frag is None:
            pass
        elif isinstance(frag, FragmentShader):
            shaders.append(frag)
        elif is_string(frag):
            shaders.append(FragmentShader(frag))
        elif isinstance(frag, (list, tuple)):
            for shader in frag:
                if is_string(shader):
                    shader = FragmentShader(shader)
                shaders.append(shader)
        else:
            raise ValueError('Invalid value for FragmentShader "%r"' % frag)

        # Attach shaders now
        if shaders:
            self.attach(*shaders)

    def __repr__(self):
        return "<%s %d>" % (self.__class__.__name__, self._id)

    def attach(self, *shaders):
        """ Attach one or more vertex/fragment shaders to the program.

        Paramaters
        ----------
        *shaders : Shader objects
            The VertexShader or FragmentShader to attach.

        """
        # Tuple or list given?
        if len(shaders) == 1 and isinstance(shaders[0], (list, tuple)):
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
        if len(shaders) == 1 and isinstance(shaders[0], (list, tuple)):
            shaders = shaders[0]

        # Process each shader
        for shader in shaders:
            if isinstance(shader, VertexShader):
                if shader in self._verts:
                    self._verts.remove(shader)
                else:
                    raise ShaderError("Shader is not attached to the program")
            elif isinstance(shader, FragmentShader):
                if shader in self._frags:
                    self._frags.remove(shader)
                else:
                    raise ShaderError("Shader is not attached to the program")
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
                logger.warn("Warning: attribute data given as a structured " +
                            "array, you probably want to use a VertexBuffer.")
                for k in vars.dtype.fields:
                    D[k] = vars[k]
            else:
                raise ValueError(
                    "Program.set_attr accepts a structured " +
                    "array, but normal arrays must be given as keyword args.")

        elif isinstance(vars, VertexBuffer):
            # Vertex buffer
            if vars.dtype.names:
                for k in vars.dtype.names:
                    if k not in self._attributes.keys():
                        logger.warn('Dropping "%s" item; '
                                    'it is not a known attribute.' % k)
                    else:
                        D[k] = vars[k]
            else:
                raise ValueError('Can only set attributes with a ' +
                                 'structured VertexBuffer.')

        elif isinstance(vars, dict):
            # Dict
            for k in vars:
                if not (k in self._attributes.keys() or
                        k in self._uniforms.keys()):
                    logger.warn('Dropping "%s" item; '
                                'it is not a known attribute/uniform.' % k)
                else:
                    D[k] = vars[k]
        else:
            raise TypeError("Don't know how to use attribute of type %r" %
                            type(vars))

        # Apply each
        for name, data in D.items():
            self[name] = data

    @property
    def attributes(self):
        """ A list of all Attribute objects associated with this program
        (sorted by name).
        """
        return list(sorted(self._attributes.values(), key=lambda x: x.name))

    @property
    def uniforms(self):
        """ A list of all Uniform objects associated with this program
        (sorted by name).
        """
        return list(sorted(self._uniforms.values(), key=lambda x: x.name))

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
                    if count != attribute.count:
                        logger.warn('Warning: attributes have unequal '
                                    'number of vertices.')
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
            # When attribute is an array, size corresponds to the highest used
            # index
            if m:
                name = m.group('name')
                if size >= 1:
                    for i in range(size):
                        name = '%s[%d]' % (m.group('name'), i)
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
            # When uniform is an array, size corresponds to the highest used
            # index
            if m:
                name = m.group('name')
                if size >= 1:
                    for i in range(size):
                        name = '%s[%d]' % (m.group('name'), i)
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

    # Behaver like a GLObject
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

        # Check if one of our shaders nees an updata.
        # If so, we force ourselve to update, which will re-attach
        # and activate all shaders.
        shaders_need_update = False
        for shader in self.shaders:
            shaders_need_update = shaders_need_update or shader._need_update

        # Update?
        if shaders_need_update:
            self._need_update = True
            # Recursive, but beware to deactivate first, or we get
            # "stuck" in a false activated state
            self._deactivate()
            self.activate()

    def _deactivate(self):
        """ Deactivate any objects that were activated on our behalf,
        and then deactivate ourself.
        """
        self._active = False
        for ob in reversed(self._activated_objects):
            ob.deactivate()
        self._activated_objects = []
        gl.glUseProgram(0)

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
            raise ProgramError('Shaders did not compile.')

        # Link the program
        # todo: should there be a try-except around this?
        gl.glLinkProgram(self._handle)
        if not gl.glGetProgramiv(self._handle, gl.GL_LINK_STATUS):
            errors = gl.glGetProgramInfoLog(self._handle)
            errormsg = self._get_error(errors, 4)
            # parse_shader_errors(errors)
            raise ProgramError('Error linking %r:\n' % self + errormsg)

        # Mark all active attributes and uniforms
        self._mark_active_attributes()
        self._mark_active_uniforms()

        # Invalidate all uniforms and attributes
        for var in self._uniforms.values():
            var.invalidate()
        for var in self._attributes.values():
            var.invalidate()

    def _get_error(self, errors, indentation=0):
        """ Get linking error in a somewhat nicer format.
        """
        # Init
        if not is_string(errors):
            errors = errors.decode('utf-8', 'replace')
        # Parse lines
        results = [line for line in errors.splitlines() if line]
        # Add indentation and return
        results = [' ' * indentation + r for r in results]
        return '\n'.join(results)

    ## Drawing and enabling
    def activate_object(self, object):
        """ Activate an object, e.g. a texture. The program
        will make sure that the object is disabled again.
        Can only be called while Program is active.
        """
        if not self._active:
            raise ProgramError(
                "Program cannot enable an object if not self being enabled.")
        object.activate()
        self._activated_objects.append(object)

    def draw(self, mode, subset=None):
        """ Draw the vertices in the specified mode.

        If the program is not active, it is activated to do the
        drawing and then deactivated.

        Parameters
        ----------
        mode : str
            POINTS, LINES, LINE_STRIP, LINE_LOOP, TRIANGLES, TRIANGLE_STRIP,
            TRIANGLE_FAN. Case insensitive. Alternatively, the real GL enum
            can also be given.
        subset : {ElementBuffer, tuple}
            The subset of vertices to draw. This can be an ElementBuffer
            that specifies the indices of the vertices to draw, or a
            tuple that specifies the slice: (start, end). The second
            element in this tuple can be None to specify the maximum
            length. If the subset is not given or None, all vertices
            are drawn.
        """

        # Check if active. If not, call recursively, but activated
        if not self._active:
            with self:
                if self._error_enter:
                    return  # Do not draw if activation went wrong!
                return self.draw(mode, subset)

        # Check mode
        mode = convert_to_enum(mode)
        if mode not in [gl.GL_POINTS, gl.GL_LINES, gl.GL_LINE_STRIP,
                        gl.GL_LINE_LOOP, gl.GL_TRIANGLES, gl.GL_TRIANGLE_STRIP,
                        gl.GL_TRIANGLE_FAN]:
            raise ValueError('Given mode is invalid: %r.' % mode)

        # Allow subset None
        if subset is None:
            subset = (0, None)

        # Upload any attributes and uniforms if necessary
        for variable in (self.attributes + self.uniforms):
            if variable.active:
                variable.upload(self)

        # Enable any other stuff
        need_enabled = set()
        for shader in self._verts + self._frags:
            need_enabled.update(shader._need_enabled)
        for enum in need_enabled:
            gl.glEnable(enum)

        if isinstance(subset, ElementBuffer):
            # Draw elements

            # Prepare pointer or offset
            if isinstance(subset, ClientElementBuffer):
                ptr = subset.data
            else:
                # Note that this can also be a ctypes.pointer offset
                ptr = None

            # Activate
            self.activate_object(subset)
            # Prepare
            gltype = ElementBuffer.DTYPE2GTYPE[subset.dtype.name]
            if gltype == gl.GL_UNSIGNED_INT and \
                    not ext_available('element_index_uint'):
                raise ValueError('element_index_uint extension needed '
                                 'for uint32 ElementBuffer.')
            # Draw
            gl.glDrawElements(mode, subset.count, gltype, ptr)

        elif isinstance(subset, tuple):
            # Draw arrays

            # Check tuple
            ok = [isinstance(i, (int, type(None))) for i in subset]
            if len(subset) != 2 or not all(ok):
                raise ValueError('Subset must be a two-element tuple with '
                                 'interegers or None.')
            # Get start, end, refcount
            start, end = subset
            start = start or 0
            refcount = self._get_vertex_count()
            # Determine count
            if end is None:
                count = refcount
                if count is None:
                    raise ProgramError(
                        "Could not determine element count for draw.")
            else:
                count = end - start
                if refcount and count > refcount:
                    raise ValueError(
                        'Count is larger than known number of vertices.')
            # Draw
            gl.glDrawArrays(mode, start, count)

        else:
            raise ValueError(
                'Given subset is of invalid type: %r.' %
                type(subset))

        # Clean up
        for enum in need_enabled:
            gl.glDisable(enum)
