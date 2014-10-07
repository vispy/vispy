# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------


"""
Implementation of a GL Program object. 

This class parses the source code to obtain the names and types of
uniforms, attributes, varyings and constants. This information is used
to provide the user with a natural way to set variables.

Gloo vs GLIR
------------

Done in this class:
  * Check the data shape given for uniforms and attributes
  * Convert uniform data to array of the correct type
  * Check whether any variables are set that are not present in source code

Done by GLIR:
  * Check whether a set uniform/attribute is not active (a warning is given)
  * Check whether anactive attribute or uniform is not set (a warning is given)


"""

import re
import numpy as np

from . import gl  # Only used for constants, no function calls here
from .globject import GLObject
from .buffer import VertexBuffer, IndexBuffer, DataBuffer
from .texture import BaseTexture, Texture2D, Texture3D, GL_SAMPLER_3D
from .wrappers import _check_conversion
from ..util import logger
from ..ext.six import string_types

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
    vert : str
        The vertex shader to be used by this program
    frag : str
        The fragment shader to be used by this program
    count : int (optional)
        The program will prepare a structured vertex buffer of count
        vertices. All attributes set using ``prog['attr'] = X`` will
        be combined into a structured vbo with interleaved elements, which
        is more efficient than having one vbo per attribute.
    
    Notes
    -----
    If several shaders are specified, only one can contain the main
    function. OpenGL ES 2.0 does not support a list of shaders.
    """
    
    _GLIR_TYPE = 'Program'
    
    _gtypes = {  # GL_TYPE, GL_BASE_TYPE, DTYPE, NUMEL
        'float':        (gl.GL_FLOAT,       gl.GL_FLOAT,    np.float32, 1),
        'vec2':         (gl.GL_FLOAT_VEC2,  gl.GL_FLOAT,    np.float32, 2),
        'vec3':         (gl.GL_FLOAT_VEC3,  gl.GL_FLOAT,    np.float32, 3),
        'vec4':         (gl.GL_FLOAT_VEC4,  gl.GL_FLOAT,    np.float32, 4),
        'int':          (gl.GL_INT,         gl.GL_INT,      np.int32,   1),
        'ivec2':        (gl.GL_INT_VEC2,    gl.GL_INT,      np.int32,   2),
        'ivec3':        (gl.GL_INT_VEC3,    gl.GL_INT,      np.int32,   3),
        'ivec4':        (gl.GL_INT_VEC4,    gl.GL_INT,      np.int32,   4),
        'bool':         (gl.GL_BOOL,        gl.GL_BOOL,     np.bool,    1),
        'bvec2':        (gl.GL_BOOL_VEC2,   gl.GL_BOOL,     np.bool,    2),
        'bvec3':        (gl.GL_BOOL_VEC3,   gl.GL_BOOL,     np.bool,    3),
        'bvec4':        (gl.GL_BOOL_VEC4,   gl.GL_BOOL,     np.bool,    4),
        'mat2':         (gl.GL_FLOAT_MAT2,  gl.GL_FLOAT,    np.float32, 4),
        'mat3':         (gl.GL_FLOAT_MAT3,  gl.GL_FLOAT,    np.float32, 9),
        'mat4':         (gl.GL_FLOAT_MAT4,  gl.GL_FLOAT,    np.float32, 16),
        # 'sampler1D':  (gl.GL_SAMPLER_1D,  gl.GL_UNSIGNED_INT, np.uint32, 1),
        'sampler2D':    (gl.GL_SAMPLER_2D,  gl.GL_UNSIGNED_INT, np.uint32, 1),
        'sampler3D':    (GL_SAMPLER_3D,     gl.GL_UNSIGNED_INT, np.uint32, 1),
    }
    
    # ---------------------------------
    def __init__(self, vert=None, frag=None, count=0):
        GLObject.__init__(self)
        
        # Init source code for vertex and fragment shader
        self._shaders = '', '' 
        
        # Init description of variables obtained from source code
        self._code_variables = {}  # name -> (kind, type, name)
        # Init user-defined data for attributes and uniforms
        self._user_variables = {}  # name -> data / buffer / texture
        # Init pending user-defined data
        self._pending_variables = {}  # name -> data
        
        # NOTE: we *could* allow vert and frag to be a tuple/list of shaders,
        # but that would complicate the GLIR implementation, and it seems 
        # unncessary
        
        # Check and set shaders
        if isinstance(vert, string_types) and isinstance(frag, string_types):
            self.set_shaders(vert, frag)
        elif not (vert is None and frag is None):
            raise ValueError('Vert and frag must either both be str or None')
        
        # Build associated structured vertex buffer if count is given.
        # This makes it easy to create a structured vertex buffer
        # without having to create a numpy array with structured dtype.
        # All assignments must be done before the GLIR commands are
        # send away for parsing (in draw) though.
        self._count = count
        self._buffer = None  # Set to None in draw()
        if self._count > 0:
            dtype = []
            for kind, type, name in self._code_variables.values():
                if kind == 'attribute':
                    _, _, dt, numel = self._gtypes[type]
                    dtype.append((name, dt, numel))
            self._buffer = np.zeros(self._count, dtype=dtype)
            self.bind(VertexBuffer(self._buffer))

    def set_shaders(self, vert, frag):
        """ Set the vertex and fragment shaders.
        
        Parameters
        ----------
        vert : str
            Source code for vertex shader.
        frag : str
            Source code for fragment shaders.
        """
        if not vert or not frag:
            raise ValueError('Vertex and fragment code must both be non-empty')
        # Store source code, send it to glir, parse the code for variables
        self._shaders = vert, frag
        self._context.glir.command('SHADERS', self._id, vert, frag)
        # All current variables become pending variables again
        for key, val in self._user_variables.items():
            self._pending_variables[key] = val
        self._user_variables = {}
        # Parse code (and process pending variables)
        self._parse_variables_from_code()
    
    @property
    def shaders(self):
        """ Source code for vertex and fragment shader
        """
        return self._shaders
    
    @property
    def variables(self):
        """ A list of the variables in use by the current program
        
        The list is obtained by parsing the GLSL source code. 
        
        Returns
        -------
        variables : list
            Each variable is represented as a tuple (kind, type, name),
            where `kind` is 'attribute', 'uniform', 'varying' or 'const'.
        """
        # Note that internally the variables are stored as a dict
        # that maps names -> tuples, for easy looking up by name.
        return list(self._code_variables.values())
    
    def _parse_variables_from_code(self):
        """ Parse uniforms, attributes and varyings from the source code.
        """
        
        # Get one string of code with comments removed
        code = '\n\n'.join(self._shaders)
        code = re.sub(r'(.*)(//.*)', r'\1', code, re.M)
        
        # Regexp to look for variable names
        var_regexp = ("\s*VARIABLE\s+(?P<type>\w+)\s+"  # type
                      "(?P<name>\w+)\s*"  # name
                      "(\[(?P<size>\d+)\])?"  # maybe size
                      "(\s*\=\s*[0-9.]+)?"  # maybe default value
                      "\s*;"  # end
                      )
        
        # Parse uniforms, attributes and varyings
        self._code_variables = {}
        for kind in ('uniform', 'attribute', 'varying', 'const'):
            regex = re.compile(var_regexp.replace('VARIABLE', kind),
                               flags=re.MULTILINE)
            for m in re.finditer(regex, code):
                size = -1
                gtype = m.group('type')  # Program._gtypes[m.group('type')]
                if m.group('size'):
                    size = int(m.group('size'))
                if size >= 1:
                    for i in range(size):
                        name = '%s[%d]' % (m.group('name'), i)
                        self._code_variables[name] = kind, gtype, name 
                else:
                    name = m.group('name')
                    self._code_variables[name] = kind, gtype, name
        
        # Now that our code variables are up-to date, we can process
        # the variables that were set but yet unknown.
        self._process_pending_variables()
    
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
            self[name] = data[name]
    
    def _process_pending_variables(self):
        """ Try to apply the variables that were set but not known yet.
        """
        # Clear our list of pending variables
        self._pending_variables, pending = {}, self._pending_variables
        # Try to apply it. On failure, it will be added again
        for name, data in pending.items():
            self[name] = data
    
    def __setitem__(self, name, data):
        """ Setting uniform or attribute data
        
        This method requires the information about the variable that we
        know from parsing the source code. If this information is not
        yet available, the data is stored in a list of pending data,
        and we attempt to set it once new shading code has been set.
        
        For uniforms, the data can represent a plain uniform or a
        sampler. In the latter case, this method accepts a Texture
        object or a numpy array which is used to update the existing
        texture. A new texture is created if necessary.

        For attributes, the data can be a tuple/float which GLSL will
        use for the value of all vertices. This method also acceps VBO
        data as a VertexBuffer object or a numpy array which is used
        to update the existing VertexBuffer. A new VertexBuffer is
        created if necessary.
        """
        
        # Deal with local buffer storage (see count argument in __init__)
        if (self._buffer is not None) and not isinstance(data, DataBuffer):
            if name in self._buffer.dtype.names:
                self._buffer[name] = data
                return
        
        if name in self._code_variables:
            kind, type, name = self._code_variables[name]
            
            if kind == 'uniform':
                if type.startswith('sampler'):
                    # Texture data; overwrite or update
                    tex = self._user_variables.get(name, None)
                    if isinstance(data, BaseTexture):
                        pass
                    elif tex and hasattr(tex, 'set_data'):
                        tex.set_data(data)
                        return
                    elif type == 'sampler2D':
                        data = Texture2D(data)
                    elif type == 'sampler2D':
                        data = Texture3D(data)
                    else:
                        assert False  # This should not happen
                    # Store and send GLIR command
                    self._user_variables[name] = data
                    self._context.glir.command('UNIFORM', self._id, 
                                               name, type, data.id)
                else:
                    # Normal uniform; convert to np array and check size
                    _, _, dtype, numel = self._gtypes[type]
                    data = np.array(data, dtype=dtype).ravel()
                    if data.ndim == 0:
                        data.shape = data.size
                    if data.size != numel:
                        raise ValueError('Uniform %r needs %i elements, '
                                         'not %i.' % (name, numel, data.size))
                    # Store and send GLIR command
                    self._user_variables[name] = data
                    self._context.glir.command('UNIFORM', self._id, 
                                               name, type, data)
            
            elif kind == 'attribute':
                # Is this a constant value per vertex
                is_constant = False
                isscalar = lambda x: isinstance(x, (float, int))
                if isscalar(data):
                    is_constant = True
                elif isinstance(data, tuple):
                    is_constant = all([isscalar(e) for e in data])
                
                if not is_constant:
                    # VBO data; overwrite or update
                    vbo = self._user_variables.get(name, None)
                    if isinstance(data, DataBuffer):
                        pass
                    elif vbo and hasattr(vbo, 'set_data'):
                        vbo.set_data(data)
                        return
                    else:
                        data = VertexBuffer(data)
                    # Store and send GLIR command
                    self._user_variables[name] = data
                    value = (data.id, data.stride, data.offset)
                    self._context.glir.command('ATTRIBUTE', self._id, 
                                               name, type, value)
                else:
                    # Single-value attribute; convert to array and check size
                    _, _, dtype, numel = self._gtypes[type]
                    data = np.array(data, dtype=dtype)
                    if data.ndim == 0:
                        data.shape = data.size
                    if data.size != numel:
                        raise ValueError('Attribute %r needs %i elements, '
                                         'not %i.' % (name, numel, data.size))
                    # Store and send GLIR command
                    self._user_variables[name] = data
                    value = tuple([0] + [i for i in data])
                    self._context.glir.command('ATTRIBUTE', self._id, 
                                               name, type, value)
            else:
                raise ValueError('Cannot set data for a %s.' % kind)
        else:
            # This variable is not defined in the current source code,
            # so we cannot establish whether this is a uniform or
            # attribute, nor check its type. Try again later.
            self._pending_variables[name] = data
    
    def __getitem__(self, name):
        """ Get user-defined data for attributes and uniforms.
        """
        if name in self._user_variables:
            return self._user_variables[name]
        elif name in self._pending_variables:
            return self._pending_variables[name]
        else:
            raise KeyError("Unknown uniform or attribute %s" % name)
    
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
        
        # Invalidate buffer (data has already been send)
        self._buffer = None
        
        # Get mode
        mode = _check_conversion(mode, _known_draw_modes)
        
        # Check leftover variables, warn, discard them
        # In GLIR we check whether all attributes are indeed set
        for name in self._pending_variables:
            logger.warn('Variable %r is given but not known.' % name)
        self._pending_variables = {}
        
        # Check attribute sizes
        attributes = [vbo for vbo in self._user_variables.values() 
                      if isinstance(vbo, DataBuffer)]
        sizes = [a.size for a in attributes]
        if len(attributes) < 1:
            raise RuntimeError('Must have at least one attribute')
        if not all(s == sizes[0] for s in sizes[1:]):
            msg = '\n'.join(['%s: %s' % (str(a), a.size) for a in attributes])
            raise RuntimeError('All attributes must have the same size, got:\n'
                               '%s' % msg)
        
        # Indexbuffer
        if isinstance(indices, IndexBuffer):
            logger.debug("Program drawing %r with index buffer" % mode)
            gltypes = {np.dtype(np.uint8): gl.GL_UNSIGNED_BYTE,
                       np.dtype(np.uint16): gl.GL_UNSIGNED_SHORT,
                       np.dtype(np.uint32): gl.GL_UNSIGNED_INT}
            selection = indices.id, gltypes[indices.dtype], indices.size
            self._context.glir.command('DRAW', self._id, mode, selection)
        elif indices is None:
            selection = 0, attributes[0].size
            logger.debug("Program drawing %r with %r" % (mode, selection))
            self._context.glir.command('DRAW', self._id, mode, selection)
        else:
            raise TypeError("Invalid index: %r (must be IndexBuffer)" %
                            indices)
        
        # Process GLIR commands
        self._context.glir.flush()
