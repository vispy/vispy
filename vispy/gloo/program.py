# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
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

from .globject import GLObject
from .buffer import VertexBuffer, IndexBuffer, DataBuffer
from .texture import BaseTexture, Texture2D, Texture3D, Texture1D, TextureCube
from ..util import logger
from .util import check_enum
from .context import get_current_canvas
from .preprocessor import preprocess

# ------------------------------------------------------------ Constants ---
REGEX_VAR = {}
for kind in ('uniform', 'attribute', 'varying', 'const', 'in', 'out'):
    REGEX_VAR[kind] = re.compile(fr"\s*{kind}\s+"  # kind of variable
                                 r"((highp|mediump|lowp)\s+)?"  # Precision (optional)
                                 r"(?P<type>\w+)\s+"  # type
                                 r"(?P<name>\w+)\s*"  # name
                                 r"(\[(?P<size>\d+)\])?"  # size (optional)
                                 r"(\s*\=\s*[0-9.]+)?"  # default value (optional)
                                 r"\s*;",  # end
                                 flags=re.MULTILINE)
    

# ------------------------------------------------------------ Shader class ---
class Shader(GLObject):
    def __init__(self, code=None):
        GLObject.__init__(self)
        if code is not None:
            self.code = code

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, code):
        self._code = preprocess(code)
        # use hardcoded offset of 0 to match other GLIR DATA commands
        self._glir.command('DATA', self._id, 0, self._code)


class VertexShader(Shader):
    _GLIR_TYPE = 'VertexShader'


class FragmentShader(Shader):
    _GLIR_TYPE = 'FragmentShader'


class GeometryShader(Shader):
    _GLIR_TYPE = 'GeometryShader'


# ----------------------------------------------------------- Program class ---
class Program(GLObject):
    """Shader program object

    A Program is an object to which shaders can be attached and linked to
    create the final program.

    Uniforms and attributes can be set using indexing: e.g.
    ``program['a_pos'] = pos_data`` and ``program['u_color'] = (1, 0, 0)``.

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

    _gtypes = {  # DTYPE, NUMEL
        'float': (np.float32, 1),
        'vec2': (np.float32, 2),
        'vec3': (np.float32, 3),
        'vec4': (np.float32, 4),
        'int': (np.int32, 1),
        'ivec2': (np.int32, 2),
        'ivec3': (np.int32, 3),
        'ivec4': (np.int32, 4),
        'bool': (np.int32, 1),
        'bvec2': (bool, 2),
        'bvec3': (bool, 3),
        'bvec4': (bool, 4),
        'mat2': (np.float32, 4),
        'mat3': (np.float32, 9), 
        'mat4': (np.float32, 16),
        'sampler1D': (np.uint32, 1),
        'sampler2D': (np.uint32, 1),
        'sampler3D': (np.uint32, 1),
        'samplerCube': (np.uint32, 1),
    }

    # ---------------------------------
    def __init__(self, vert=None, frag=None, count=0):
        GLObject.__init__(self)

        # Init source code for vertex and fragment shader
        self._shaders = None, None

        # Init description of variables obtained from source code
        self._code_variables = {}  # name -> (kind, type_, name)
        # Init user-defined data for attributes and uniforms
        self._user_variables = {}  # name -> data / buffer / texture
        # Init pending user-defined data
        self._pending_variables = {}  # name -> data

        # NOTE: we *could* allow vert and frag to be a tuple/list of shaders,
        # but that would complicate the GLIR implementation, and it seems
        # unncessary

        # Check and set shaders
        if isinstance(vert, str) and isinstance(frag, str):
            self.set_shaders(vert, frag)
        elif not (vert is None and frag is None):
            raise ValueError('Vert and frag must either both be str or None')

        # Build associated structured vertex buffer if count is given.
        # This makes it easy to create a structured vertex buffer
        # without having to create a numpy array with structured dtype.
        # All assignments must be done before the GLIR commands are
        # sent away for parsing (in draw) though.
        self._count = count
        self._buffer = None  # Set to None in draw()
        if self._count > 0:
            dtype = []
            for kind, type_, name, size in self._code_variables.values():
                if kind == 'attribute':
                    dt, numel = self._gtypes[type_]
                    dtype.append((name, dt, numel) if numel != 1 else (name, dt))
            self._buffer = np.zeros(self._count, dtype=dtype)
            self.bind(VertexBuffer(self._buffer))

    def set_shaders(self, vert, frag, geom=None, update_variables=True):
        """Set the vertex and fragment shaders.

        Parameters
        ----------
        vert : str
            Source code for vertex shader.
        frag : str
            Source code for fragment shaders.
        geom : str (optional)
            Source code for geometry shader.
        update_variables : bool
            If True, then process any pending variables immediately after
            setting shader code. Default is True.
        """
        if not vert or not frag:
            raise ValueError('Vertex and fragment code must both be non-empty')

        # pre-process shader code for #include directives
        shaders = [VertexShader(vert), FragmentShader(frag)]
        if geom is not None:
            shaders.append(GeometryShader(geom))

        for shader in shaders:
            self.glir.associate(shader.glir)
            self._glir.command('ATTACH', self._id, shader.id)

        # Store source code, send it to glir, parse the code for variables
        self._shaders = shaders

        # Link all shaders into one program. All shaders are detached after
        # linking is complete.
        self._glir.command('LINK', self._id)

        # Delete shaders. We no longer need them and it frees up precious GPU
        # memory: http://gamedev.stackexchange.com/questions/47910
        for shader in shaders:
            shader.delete()

        # All current variables become pending variables again
        for key, val in self._user_variables.items():
            self._pending_variables[key] = val
        self._user_variables = {}
        # Parse code (and process pending variables)
        self._parse_variables_from_code(update_variables=update_variables)

    @property
    def shaders(self):
        """All currently attached shaders"""
        return self._shaders

    @property
    def variables(self):
        """A list of the variables in use by the current program

        The list is obtained by parsing the GLSL source code.

        Returns
        -------
        variables : list
            Each variable is represented as a tuple (kind, type, name),
            where `kind` is 'attribute', 'uniform', 'uniform_array',
            'varying' or 'const'.
        """
        # Note that internally the variables are stored as a dict
        # that maps names -> tuples, for easy looking up by name.
        return [x[:3] for x in self._code_variables.values()]

    def _parse_variables_from_code(self, update_variables=True):
        """Parse uniforms, attributes and varyings from the source code."""
        # Get one string of code with comments removed
        code = '\n\n'.join([sh.code for sh in self._shaders])
        code = re.sub(r'(.*)(//.*)', r'\1', code, re.M)

        # Parse uniforms, attributes and varyings
        self._code_variables = {}
        for kind in ('uniform', 'attribute', 'varying', 'const', 'in', 'out'):

            # pick regex for the correct kind of var
            reg = REGEX_VAR[kind]

            # treat *in* like attribute, *out* like varying
            if kind == 'in':
                kind = 'attribute'
            elif kind == 'out':
                kind = 'varying'

            for m in re.finditer(reg, code):
                gtype = m.group('type')
                size = int(m.group('size')) if m.group('size') else -1
                this_kind = kind
                if size >= 1:
                    # uniform arrays get added both as individuals and full
                    for i in range(size):
                        name = '%s[%d]' % (m.group('name'), i)
                        self._code_variables[name] = kind, gtype, name, -1
                    this_kind = 'uniform_array'
                name = m.group('name')
                self._code_variables[name] = this_kind, gtype, name, size

        # Now that our code variables are up-to date, we can process
        # the variables that were set but yet unknown.
        if update_variables:
            self._process_pending_variables()

    def bind(self, data):
        """Bind a VertexBuffer that has structured data

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
        """Try to apply the variables that were set but not known yet."""
        # Clear our list of pending variables
        self._pending_variables, pending = {}, self._pending_variables
        # Try to apply it. On failure, it will be added again
        for name, data in pending.items():
            self[name] = data

    def __setitem__(self, name, data):
        """Setting uniform or attribute data

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

        By passing None as data, the uniform or attribute can be
        "unregistered". This can be useful to get rid of variables that
        are no longer present or active in the new source code that is
        about to be set.
        """
        # Deal with local buffer storage (see count argument in __init__)
        if (self._buffer is not None) and not isinstance(data, DataBuffer):
            if name in self._buffer.dtype.names:
                self._buffer[name] = data
                return

        # Forget any pending values for this variable
        self._pending_variables.pop(name, None)

        # Delete?
        if data is None:
            self._user_variables.pop(name, None)
            return

        if name in self._code_variables:
            kind, type_, name, size = self._code_variables[name]

            if kind == 'uniform':
                if type_.startswith('sampler'):
                    # Texture data; overwrite or update
                    tex = self._user_variables.get(name, None)
                    if isinstance(data, BaseTexture):
                        pass
                    elif tex and hasattr(tex, 'set_data'):
                        tex.set_data(data)
                        return
                    elif type_ == 'sampler1D':
                        data = Texture1D(data)
                    elif type_ == 'sampler2D':
                        data = Texture2D(data)
                    elif type_ == 'sampler3D':
                        data = Texture3D(data)
                    elif type_ == 'samplerCube':
                        data = TextureCube(data)
                    else:
                        # This should not happen
                        raise RuntimeError('Unknown type %s' % type_)
                    # Store and send GLIR command
                    self._user_variables[name] = data
                    self.glir.associate(data.glir)
                    self._glir.command('TEXTURE', self._id, name, data.id)
                else:
                    # Normal uniform; convert to np array and check size
                    dtype, numel = self._gtypes[type_]
                    data = np.array(data, dtype=dtype).ravel()
                    if data.size != numel:
                        raise ValueError('Uniform %r needs %i elements, '
                                         'not %i.' % (name, numel, data.size))
                    # Store and send GLIR command
                    self._user_variables[name] = data
                    self._glir.command('UNIFORM', self._id, name, type_, data)

            elif kind == 'uniform_array':
                # Normal uniform; convert to np array and check size
                dtype, numel = self._gtypes[type_]
                data = np.atleast_2d(data).astype(dtype)
                need_shape = (size, numel)
                if data.shape != need_shape:
                    raise ValueError('Uniform array %r needs shape %s not %s'
                                     % (name, need_shape, data.shape))
                data = data.ravel()
                # Store and send GLIR command
                self._user_variables[name] = data
                self._glir.command('UNIFORM', self._id, name, type_, data)

            elif kind == 'attribute':
                # Is this a constant value per vertex
                is_constant = False

                def isscalar(x):
                    return isinstance(x, (float, int))

                if isscalar(data):
                    is_constant = True
                elif isinstance(data, (tuple, list)):
                    is_constant = all([isscalar(e) for e in data])

                if not is_constant:
                    # VBO data; overwrite or update
                    vbo = self._user_variables.get(name, None)
                    if isinstance(data, DataBuffer):
                        pass
                    elif vbo is not None and hasattr(vbo, 'set_data'):
                        vbo.set_data(data)
                        return
                    else:
                        data = VertexBuffer(data)
                    # Store and send GLIR command
                    if data.dtype is not None:
                        numel = self._gtypes[type_][1]
                        if data._last_dim and data._last_dim != numel:
                            raise ValueError('data.shape[-1] must be %s '
                                             'not %s for %s'
                                             % (numel, data._last_dim, name))
                    divisor = getattr(data, 'divisor', None)
                    self._user_variables[name] = data
                    value = (data.id, data.stride, data.offset)
                    self.glir.associate(data.glir)
                    self._glir.command('ATTRIBUTE', self._id,
                                       name, type_, value, divisor)
                else:
                    # Single-value attribute; convert to array and check size
                    dtype, numel = self._gtypes[type_]
                    data = np.array(data, dtype=dtype)
                    if data.ndim == 0:
                        data.shape = data.size
                    if data.size != numel:
                        raise ValueError('Attribute %r needs %i elements, '
                                         'not %i.' % (name, numel, data.size))
                    divisor = getattr(data, 'divisor', None)
                    # Store and send GLIR command
                    self._user_variables[name] = data
                    value = tuple([0] + [i for i in data])
                    self._glir.command('ATTRIBUTE', self._id,
                                       name, type_, value, divisor)
            else:
                raise KeyError('Cannot set data for a %s.' % kind)
        else:
            # This variable is not defined in the current source code,
            # so we cannot establish whether this is a uniform or
            # attribute, nor check its type. Try again later.
            self._pending_variables[name] = data

    def __contains__(self, key):
        return key in self._code_variables

    def __getitem__(self, name):
        """Get user-defined data for attributes and uniforms."""
        if name in self._user_variables:
            return self._user_variables[name]
        elif name in self._pending_variables:
            return self._pending_variables[name]
        else:
            raise KeyError("Unknown uniform or attribute %s" % name)

    def draw(self, mode='triangles', indices=None, check_error=True):
        """Draw the attribute arrays in the specified mode.

        Parameters
        ----------
        mode : str | GL_ENUM
            'points', 'lines', 'line_strip', 'line_loop', 'lines_adjacency',
            'line_strip_adjacency', 'triangles', 'triangle_strip', or
            'triangle_fan'.
        indices : array
            Array of indices to draw.
        check_error:
            Check error after draw.
        """
        # Invalidate buffer (data has already been sent)
        self._buffer = None

        # Check if mode is valid
        mode = check_enum(mode)
        if mode not in ['points', 'lines', 'line_strip', 'line_loop',
                        'lines_adjacency', 'line_strip_adjacency', 'triangles',
                        'triangle_strip', 'triangle_fan']:
            raise ValueError('Invalid draw mode: %r' % mode)

        # Check leftover variables, warn, discard them
        # In GLIR we check whether all attributes are indeed set
        for name in self._pending_variables:
            logger.warn('Value provided for %r, but this variable was not '
                        'found in the shader program.' % name)
        self._pending_variables = {}

        # Check attribute sizes
        attributes = [vbo for vbo in self._user_variables.values()
                      if isinstance(vbo, DataBuffer)]

        attrs = [a for a in attributes if getattr(a, 'divisor', None) is None]
        if len(attrs) < 1:
            raise RuntimeError('Must have at least one attribute')
        sizes = [a.size for a in attrs]
        if not all(s == sizes[0] for s in sizes[1:]):
            msg = '\n'.join([f'{str(a)}: {a.size}' for a in attrs])
            raise RuntimeError('All attributes must have the same size, got:\n{msg}')

        attrs_with_div = [a for a in attributes if a not in attrs]
        if attrs_with_div:
            sizes = [a.size for a in attrs_with_div]
            divs = [a.divisor for a in attrs_with_div]
            instances = sizes[0] * divs[0]
            if not all(s * d == instances for s, d in zip(sizes, divs)):
                msg = '\n'.join([f'{str(a)}: {a.size} * {a.divisor} = {a.size * a.divisor}' for a in attrs_with_div])
                raise RuntimeError(f'All attributes with divisors must have the same size as the number of instances, got:\n{msg}')
        else:
            instances = 1

        # Get the glir queue that we need now
        canvas = get_current_canvas()
        assert canvas is not None

        # Associate canvas
        canvas.context.glir.associate(self.glir)

        # Indexbuffer
        if isinstance(indices, IndexBuffer):
            canvas.context.glir.associate(indices.glir)
            logger.debug("Program drawing %r with index buffer" % mode)
            gltypes = {np.dtype(np.uint8): 'UNSIGNED_BYTE',
                       np.dtype(np.uint16): 'UNSIGNED_SHORT',
                       np.dtype(np.uint32): 'UNSIGNED_INT'}
            selection = indices.id, gltypes[indices.dtype], indices.size
            canvas.context.glir.command('DRAW', self._id, mode, selection, instances)
        elif indices is None:
            selection = 0, attributes[0].size
            logger.debug("Program drawing %r with %r" % (mode, selection))
            canvas.context.glir.command('DRAW', self._id, mode, selection, instances)
        else:
            raise TypeError("Invalid index: %r (must be IndexBuffer)" %
                            indices)

        # Process GLIR commands
        canvas.context.flush_commands()
