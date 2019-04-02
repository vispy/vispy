"""PyScript module for gloo2.js - lightweight object oriented GL."""

from flexx.pyscript import this_is_js, window

if this_is_js():  # noqa - fool flake8
    console = window.console

__version__ = '0.3'


def check_error(gl, when='periodic check'):
    """Check this from time to time to detect GL errors.

    Parameters
    ----------
    when : str
        Shown in the exception to help the developer determine when
        this check was done.
    """
    errors = []
    while True:
        err = gl.getError()
        if err == gl.NO_ERROR or (errors and err == errors[-1]):
            break
        errors.append(err)
    if len(errors):
        msg = ''
        for e in errors:
            msg += e
        raise RuntimeError('OpenGL got errors (%s): %s' % (when, msg))


class GlooObject(object):
    """Abstract base class for all Gloo classes."""
    
    def __init__(self, gl):
        """Init by passing the webgl context object."""
        self._gl = gl
        self.handle = None  # should be set in _init()
        self._create()
        assert self.handle is not None

    def _create(self):
        raise NotImplementedError()


class Program(GlooObject):
    """The program is the central component to connect gloo objects and shaders."""
    
    UTYPEMAP = {
        'float': 'uniform1fv',
        'vec2': 'uniform2fv',
        'vec3': 'uniform3fv',
        'vec4': 'uniform4fv',
        'int': 'uniform1iv',
        'ivec2': 'uniform2iv',
        'ivec3': 'uniform3iv',
        'ivec4': 'uniform4iv',
        'bool': 'uniform1iv',
        'bvec2': 'uniform2iv',
        'bvec3': 'uniform3iv',
        'bvec4': 'uniform4iv',
        'mat2': 'uniformMatrix2fv',
        'mat3': 'uniformMatrix3fv',
        'mat4': 'uniformMatrix4fv',
        'sampler1D': 'uniform1i',
        'sampler2D': 'uniform1i',
        'sampler3D': 'uniform1i',
    }
    
    ATYPEMAP = {
        'float': 'vertexAttrib1f',
        'vec2': 'vertexAttrib2f',
        'vec3': 'vertexAttrib3f',
        'vec4': 'vertexAttrib4f',
    }
    
    ATYPEINFO = {
        'float': (1, 5126),
        'vec2': (2, 5126),
        'vec3': (3, 5126),
        'vec4': (4, 5126),
    }
    
    def _create(self):
        self.handle = self._gl.createProgram()
        self.locations = {}
        self._unset_variables = []
        self._validated = False
        self._samplers = {}  # name -> (tex-target, tex-handle, unit)
        self._attributes = {}  # name -> (vbo-handle, attr-handle, func, args)
        self._known_invalid = []
    
    def delete(self):
        """Delete the program."""
        self._gl.deleteProgram(self.handle)
    
    def activate(self):
        """Activate the program."""
        self._gl.useProgram(self.handle)
    
    def deactivate(self):
        """Disable the program."""
        self._gl.useProgram(0)
    
    def set_shaders(self, vert, frag):
        """Set GLSL code for the vertex and fragment shader.
        
        This function takes care of setting the shading code and
        compiling+linking it into a working program object that is ready
        to use.
        
        Parameters
        ----------
        vert : str
            GLSL code for the vertex shader.
        frag : str
            GLSL code for the fragment shader.
        """
        gl = self._gl
        self._linked = False
        # Create temporary shader objects
        vert_handle = gl.createShader(gl.VERTEX_SHADER)
        frag_handle = gl.createShader(gl.FRAGMENT_SHADER)
        # For both vertex and fragment shader: set source, compile, check
        tmp = [(vert, vert_handle, 'vertex'), (frag, frag_handle, 'fragment')]
        for i in range(2):
            code, handle, type_ = tmp[i]
            gl.shaderSource(handle, code)
            gl.compileShader(handle)
            status = gl.getShaderParameter(handle, gl.COMPILE_STATUS)
            if not status:
                errors = gl.getShaderInfoLog(handle)
                raise RuntimeError('errors in ' + type_ + ' shader:\n' + errors)
        # Attach shaders
        gl.attachShader(self.handle, vert_handle)
        gl.attachShader(self.handle, frag_handle)
        # Link the program and check
        gl.linkProgram(self.handle)
        if not gl.getProgramParameter(self.handle, gl.LINK_STATUS):
            raise RuntimeError("Program link error:\n" + 
                               gl.getProgramInfoLog(self.handle))
        # Now we know what variables will be used by the program. Do *before* 
        # cleanup, otherwise https://github.com/bokeh/bokeh/issues/2683
        self._unset_variables = self._get_active_attributes_and_uniforms()
        # Now we can remove the shaders. We no longer need them and it frees up
        # precious GPU memory:http://gamedev.stackexchange.com/questions/47910
        gl.detachShader(self.handle, vert_handle)
        gl.detachShader(self.handle, frag_handle)
        gl.deleteShader(vert_handle)
        gl.deleteShader(frag_handle)
        # Set / reset
        self._known_invalid = []
        self._linked = True
    
    def _get_active_attributes_and_uniforms(self):
        """
        Retrieve active attributes and uniforms to be able to check that
        all uniforms/attributes are set by the user.
        """
        gl = self._gl
        self.locations = {}
        # This match a name of the form "name[size]" (= array)
        regex = window.RegExp("(\\w+)\\s*(\\[(\\d+)\\])\\s*")
        # Get how many active attributes and uniforms there are
        cu = gl.getProgramParameter(self.handle, gl.ACTIVE_UNIFORMS)
        ca = gl.getProgramParameter(self.handle, gl.ACTIVE_ATTRIBUTES)
        # Get info on each one
        attributes = []
        uniforms = []
        for x in [(attributes, ca, gl.getActiveAttrib, gl.getAttribLocation),
                  (uniforms, cu, gl.getActiveUniform, gl.getUniformLocation)]:
            container, count, getActive, getLocation = x
            for i in range(count):
                info = getActive.call(gl, self.handle, i)
                name = info.name
                m = name.match(regex)  # Check if xx[0] instead of xx
                if m:
                    # Note that info.size can smaller than what is defined in
                    # GLSL; the compiler might know that only xx[0] is used. 
                    name = m[1]
                    for j in range(info.size):
                        container.append(('%s[%d]' % (name, j), info.type))
                else:
                    container.append((name, info.type))
                self.locations[name] = getLocation.call(gl, self.handle, name)
        return [v[0] for v in attributes] + [v[0] for v in uniforms]
    
    def set_texture(self, name, value):
        """Set a texture sampler.
        
        A texture is a 2 dimensional grid of colors/intensities that
        can be applied to a face (or used for other means by providing
        a regular grid of data).
        
        Parameters
        ----------
        name : str
            The name by which the texture is known in the GLSL code.
        value : Texture2D
            The gloo Texture2D object to bind.
        """
        if not self._linked:
            raise RuntimeError('Cannot set uniform when program has no code')
        # Get handle for the uniform
        handle = self.locations.get(name, -1)
        if handle < 0:
            if name not in self._known_invalid:
                self._known_invalid.append(name)
                console.log('Variable %s is not an active texture' % name)
            return
        # Mark as set
        if name in self._unset_variables:
            self._unset_variables.remove(name)
        # Program needs to be active in order to set uniforms
        self.activate()
        if True:
            # Sampler: the value is the texture object
            unit = len(self._samplers.keys())
            if name in self._samplers:
                unit = self._samplers[name][-1]  # Use existing unit            
            self._samplers[name] = value._target, value.handle, unit  # noqa
            self._gl.uniform1i(handle, unit)
    
    def set_uniform(self, name, type_, value):
        """Set a uniform value.
        
        A uniform is a value that is global to both the vertex and
        fragment shader.
        
        Parameters
        ----------
        name : str
            The name by which the uniform is known in the GLSL code.
        type_ : str
            The type of the uniform, e.g. 'float', 'vec2', etc.
        value : list of scalars
            The value for the uniform. Should be a list even for type float.
        """
        if not self._linked:
            raise RuntimeError('Cannot set uniform when program has no code')
        # Get handle for the uniform
        handle = self.locations.get(name, -1)
        if handle < 0:
            if name not in self._known_invalid:
                self._known_invalid.append(name)
                console.log('Variable %s is not an active uniform' % name)
            return
        # Mark as set
        if name in self._unset_variables:
            self._unset_variables.remove(name)
        count = 1
        if not type_.startswith('mat'):
            a_type = {'int': 'float', 'bool': 'float'}.get(type_, type_.lstrip('ib'))
            count = value.length // (self.ATYPEINFO[a_type][0])
        if count > 1:
            for j in range(count):
                if '%s[%s]' % (name, j) in self._unset_variables:
                    name_ = '%s[%s]' % (name, j)
                    if name_ in self._unset_variables:
                        self._unset_variables.remove(name_)
        # Look up function to call
        funcname = self.UTYPEMAP[type_]
        # Program needs to be active in order to set uniforms
        self.activate()
        if type_.startswith('mat'):
            self._gl[funcname](handle, False, value)
        else:
            self._gl[funcname](handle, value)
    
    def set_attribute(self, name, type_, value, stride=0, offset=0):
        """Set an attribute value. 
        
        An attribute represents per-vertex data and can only be used
        in the vertex shader.
        
        Parameters
        ----------
        name : str
            The name by which the attribute is known in the GLSL code.
        type_ : str
            The type of the attribute, e.g. 'float', 'vec2', etc.
        value : VertexBuffer, array
            If value is a VertexBuffer, it is used (with stride and offset)
            for the vertex data. If value is an array, its used to set
            the value of all vertices (similar to a uniform).
        stide : int, default 0
            The stride to "sample" the vertex data inside the buffer. Unless
            multiple vertex data are packed into a single buffer, this should
            be zero.
        offset : int, default 0
            The offset to "sample" the vertex data inside the buffer. Unless
            multiple vertex data are packed into a single buffer, or only
            a part of the data must be used, this should probably be zero.
        """
        if not self._linked:
            raise RuntimeError('Cannot set attribute when program has no code')
        is_vbo = isinstance(value, VertexBuffer)
        
        # Get handle for the attribute, first try cache
        handle = self.locations.get(name, -1)
        if handle < 0:
            if name not in self._known_invalid:
                self._known_invalid.append(name)
                if is_vbo and offset > 0:
                    pass  # Probably an unused element in a structured VBO
                else:
                    console.log('Variable %s is not an active attribute' % name)
            return
        # Mark as set
        if name in self._unset_variables:
            self._unset_variables.remove(name)
        # Program needs to be active in order to set uniforms
        self.activate()
        # Triage depending on VBO or tuple data
        if not is_vbo:
            funcname = self.ATYPEMAP[type_]
            self._attributes[name] = 0, handle, funcname, value
        else:
            size, gtype = self.ATYPEINFO[type_]
            funcname = 'vertexAttribPointer'
            args = size, gtype, self._gl.FALSE, stride, offset
            self._attributes[name] = value.handle, handle, funcname, args

    def _pre_draw(self):
        """Prepare for drawing."""
        self.activate()
        # Activate textures
        for x in self._samplers.values():
            tex_target, tex_handle, unit = x
            self._gl.activeTexture(self._gl.TEXTURE0 + unit)
            self._gl.bindTexture(tex_target, tex_handle)
        # Activate attributes
        for x in self._attributes.values():
            vbo_handle, attr_handle, funcname, args = x
            if vbo_handle:
                self._gl.bindBuffer(self._gl.ARRAY_BUFFER, vbo_handle)
                self._gl.enableVertexAttribArray(attr_handle)
                self._gl[funcname](attr_handle, *args)
            else:
                self._gl.bindBuffer(self._gl.ARRAY_BUFFER, None)
                self._gl.disableVertexAttribArray(attr_handle)
                self._gl[funcname](attr_handle, *args)
        # Validate. We need to validate after textures units get assigned
        if not self._validated:
            self._validated = True
            self._validate()
    
    def _validate(self):
        # Validate ourselves
        if len(self._unset_variables):
            console.log('Program has unset variables: %s' % self._unset_variables)
        # Validate via OpenGL
        self._gl.validateProgram(self.handle)
        if not self._gl.getProgramParameter(self.handle, 
                                            self._gl.VALIDATE_STATUS):
            console.log(self._gl.getProgramInfoLog(self.handle))
            raise RuntimeError('Program validation error')
    
    def draw(self, mode, selection):
        """Draw the current visualization defined by the program.
        
        Parameters
        ----------
        mode : GL enum
            Can be POINTS, LINES, LINE_LOOP, LINE_STRIP, LINE_FAN, TRIANGLES
        selection : 2-element tuple or IndexBuffer
            The selection to draw, specified either as (first, count) or an
            IndexBuffer object.
        """
        if not self._linked:
            raise RuntimeError('Cannot draw program if code has not been set')
        # Init
        check_error(self._gl, 'before draw')
        # Draw
        if isinstance(selection, IndexBuffer):
            self._pre_draw()
            selection.activate()
            count = selection._buffer_size / 2  # noqa
            gtype = self._gl.UNSIGNED_SHORT
            self._gl.drawElements(mode, count, gtype, 0)
            selection.deactivate()
        else:
            # Selection based on start and count
            first, count = selection
            if count:
                self._pre_draw()
                self._gl.drawArrays(mode, first, count)
        # Wrap up
        check_error(self._gl, 'after draw')


class Buffer(GlooObject):
    """Base buffer class for vertex data or index data."""
    
    _target = None
    _usage = 35048  # DYNAMIC_DRAW - STATIC_DRAW, STREAM_DRAW or DYNAMIC_DRAW
    
    def _create(self):
        self.handle = self._gl.createBuffer()
        self._buffer_size = 0
    
    def delete(self):
        """Delete the buffer."""
        self._gl.deleteBuffer(self.handle)
    
    def activate(self):
        """Activete the buffer."""
        self._gl.bindBuffer(self._target, self.handle)
    
    def deactivate(self):
        """Disable the buffer."""
        self._gl.bindBuffer(self._target, None)
    
    def set_size(self, nbytes):
        """Set the size of the buffer in bytes.
        
        Parameters
        ----------
        nbytes : int
            The number of bytes that the buffer needs to hold.
        """
        # Note: for attributes we always have 32 bit data, and for indices 16 bit
        if nbytes != self._buffer_size:
            self.activate()
            self._gl.bufferData(self._target, nbytes, self._usage)
            self._buffer_size = nbytes
    
    def set_data(self, offset, data):
        """Set the buffer data.
        
        Parameters
        ----------
        offset : int
            The offset in bytes for the new data.
        data : typed array
            The data to upload.
        """
        self.activate()
        # nbytes = len(data) * data.BYTES_PER_ELEMENT
        self._gl.bufferSubData(self._target, offset, data)


class VertexBuffer(Buffer):
    """A buffer for vertex data."""
    
    _target = 34962  # ARRAY_BUFFER
    

class IndexBuffer(Buffer):
    """A buffer for index data."""
    
    _target = 34963  # ELEMENT_ARRAY_BUFFER


class Texture2D(GlooObject):
    """A 2 dimensional regular grid."""
    
    _target = 3553  # TEXTURE_2D
    
    _types = {
        'Int8Array': 5120,  # BYTE,
        'Uint8Array': 5121,  # UNSIGNED_BYTE,
        'Int16Array': 5122,  # SHORT,
        'Uint16Array': 5123,  # UNSIGNED_SHORT,
        'Int32Array': 5124,  # INT,
        'Uint32Array': 5125,  # UNSIGNED_INT,
        # 'xx' : gl.GL_HALF_FLOAT,
        'Float32Array': 5126,  # FLOAT,
        # 'Float64Array' : gl.GL_DOUBLE
    }
    
    def _create(self):
        self.handle = self._gl.createTexture()
        self._shape_format = None  # To make setting size cheap
    
    def delete(self):
        """Delete the texture."""
        self._gl.deleteTexture(self.handle)
    
    def activate(self):
        """Activate the texture."""
        self._gl.bindTexture(self._target, self.handle)
    
    def deactivate(self):
        """Disable the texture."""
        self._gl.bindTexture(self._target, 0)
    
    # Taken from pygly
    def _get_alignment(self, width):
        """Determines a textures byte alignment. If the width isn't a
        power of 2 we need to adjust the byte alignment of the image.
        The image height is unimportant.

        www.opengl.org/wiki/Common_Mistakes#Texture_upload_and_pixel_reads
        """
        # We know the alignment is appropriate if we can divide the
        # width by the alignment. Calid alignments are 1,2,4,8.
        # Put 4 first, since it's the default
        alignments = [4, 8, 2, 1]
        for alignment in alignments:
            if width % alignment == 0:
                return alignment
    
    def set_wrapping(self, wrap_s, wrap_t):
        """Set the texture wrapping mode.
        
        Parameters
        ----------
        wrap_s : GL enum
            The mode to wrap the x dimension. Valid values are REPEAT
            CLAMP_TO_EDGE MIRRORED_REPEAT
        wrap_t : GL enum
            The mode to wrap the y dimension. Same options as for wrap_s.
        """
        self.activate()
        self._gl.texParameterf(self._target, self._gl.TEXTURE_WRAP_S, wrap_s)
        self._gl.texParameterf(self._target, self._gl.TEXTURE_WRAP_T, wrap_t)
    
    def set_interpolation(self, min, mag):
        """Set the texture interpolation mode
        
        Parameters
        ----------
        min : GL enum
            The interpolation mode when minifying (i.e. zoomed out). Valid
            values are LINEAR and NEAREST.
        max : GL enum
            The interpolation mode when magnifying (i.e. zoomed in). Valid
            values are LINEAR, NEAREST, NEAREST_MIPMAP_NEAREST,
            LINEAR_MIPMAP_NEAREST, NEAREST_MIPMAP_LINEAR, LINEAR_MIPMAP_LINEAR.
        """
        self.activate()
        self._gl.texParameterf(self._target, self._gl.TEXTURE_MIN_FILTER, min)
        self._gl.texParameterf(self._target, self._gl.TEXTURE_MAG_FILTER, mag)
    
    def set_size(self, shape, format):
        """Set the size of the 2D texture.
        
        Parameters
        ----------
        shape : tuple of ints
            The shape of the data to upload
        format : GL enum
            The format of the texture data. Can be LUMINANCE, LUMINANCE_ALPHA,
            RGB, and RGBA.
        """
        # Shape is height, width
        height, width = shape
        if (height, width, format) != self._shape_format:
            self._shape_format = height, width, format
            self.activate()
            self._gl.texImage2D(self._target, 0, format, width, height, 0, format, 
                                self._gl.UNSIGNED_BYTE, None)
        self.u_shape = height, width  # for uniform
    
    def set_data(self, offset, shape, data):
        """Set the 2D texture data.
        
        Parameters
        ----------
        offset : tuple of ints
            Offset in pixels for each dimension.
        shape : tuple of ints
            The shape of the data to upload
        data : typed array
            The actual pixel data. Can be of any type, but on the GPU the
            dat is stored in 8 bit precision.
        """
        if len(shape) == 2:
            shape = shape[0], shape[1], 1
        self.activate()
        format = self._shape_format[2]
        height, width, _ = shape
        y, x = offset
        # Get gtype
        gtype = self._types.get(data.constructor.name, None)
        if gtype is None:
            raise ValueError("Type %s not allowed for texture" % 
                             data.constructor.name)
        # Set alignment (width is nbytes_per_pixel * npixels_per_line)
        alignment = self._get_alignment(shape[-2] * shape[-1])
        if alignment != 4:
            self._gl.pixelStorei(self._gl.UNPACK_ALIGNMENT, alignment)
        # Upload
        self._gl.texSubImage2D(self._target, 0, x, y, width, height, 
                               format, gtype, data)
        if alignment != 4:
            self._gl.pixelStorei(self._gl.UNPACK_ALIGNMENT, 4)


class Texture3DLike(Texture2D):
    """A 2D texture with support to simulate a 3D texture.
    
    To use this class, use set_size() and set_data() as if it was a 3D
    texture. Add the GLSL_SAMPLE_NEAREST or GLSL_SAMPLE_LINEAR to the
    shader to add the sample3D() function that can be used instead of
    texture2D(). This function needs ``shape`` and ``tiles`` arguments
    which can be set via uniforms, using the ``u_shape`` and ``u_tiles``
    attributes of this object.
    """
    
    # The algorithms and code for this class are based on work by Irwin Zaid
    # in the Vispy project.
    
    # todo: the last slice looks weird
    # todo: should z be rounded or floored in nearest?
    
    # These GLSL snippetys uses xyz, but are really agnostic about the
    # semantic meaning of the dimensions. The semantic meaning is defined by
    # the order of the texture coordinates. Shape is reversed here, because
    # texture data is uploaded in row-major making the shape (z, y, x).
    
    GLSL_SAMPLE_NEAREST = """
        vec4 sample3D(sampler2D tex, vec3 texcoord, vec3 shape, vec2 tiles) {
            shape.xyz = shape.zyx;  // silly row-major convention
            float nrows = tiles.y, ncols = tiles.x;
            // Don't let adjacent frames be interpolated into this one
            texcoord.x = min(texcoord.x * shape.x, shape.x - 0.5);
            texcoord.x = max(0.5, texcoord.x) / shape.x;
            texcoord.y = min(texcoord.y * shape.y, shape.y - 0.5);
            texcoord.y = max(0.5, texcoord.y) / shape.y;

            float zindex = floor(texcoord.z * shape.z);

            // Do a lookup in the 2D texture
            float u = (mod(zindex, ncols) + texcoord.x) / ncols;
            float v = (floor(zindex / ncols) + texcoord.y) / nrows;

            return texture2D(tex, vec2(u,v));
        }
    """

    GLSL_SAMPLE_LINEAR = """
        vec4 sample3D(sampler2D tex, vec3 texcoord, vec3 shape, vec2 tiles) {
            shape.xyz = shape.zyx;  // silly row-major convention
            float nrows = tiles.y, ncols = tiles.x;
            // Don't let adjacent frames be interpolated into this one
            texcoord.x = min(texcoord.x * shape.x, shape.x - 0.5);
            texcoord.x = max(0.5, texcoord.x) / shape.x;
            texcoord.y = min(texcoord.y * shape.y, shape.y - 0.5);
            texcoord.y = max(0.5, texcoord.y) / shape.y;

            float z = texcoord.z * shape.z;
            float zindex1 = floor(z);
            float u1 = (mod(zindex1, ncols) + texcoord.x) / ncols;
            float v1 = (floor(zindex1 / ncols) + texcoord.y) / nrows;

            float zindex2 = zindex1 + 1.0;
            float u2 = (mod(zindex2, ncols) + texcoord.x) / ncols;
            float v2 = (floor(zindex2 / ncols) + texcoord.y) / nrows;

            vec4 s1 = texture2D(tex, vec2(u1, v1));
            vec4 s2 = texture2D(tex, vec2(u2, v2));

            return s1 * (zindex2 - z) + s2 * (z - zindex1);
        }
    """
    
    def _get_tile_info(self, shape):
        # The volume is packed in as many tiles (xy slices) as there
        # are samples in the z-axis. We'd prefer a single column, so
        # the data is contiguous, but this may not be possible due to
        # the max texture size. In that case we use multiple columns.
        
        max_size = self._gl.getParameter(self._gl.MAX_TEXTURE_SIZE)
        
        # Number of rows that we can can fit based on the size of one slice
        nrows = max_size // shape[1]
        nrows = min(nrows, shape[0])
        # Number of columns that we need with this number of columns
        ncols = window.Math.ceil(shape[0] / nrows)
        
        if ncols * shape[2] > max_size:
            raise RuntimeError('Cannot fit 3D data with shape %s onto simulated 2D texture.' % shape)
        return nrows, ncols
    
    def set_size(self, shape, format):
        """Set the size of the 3D texture.
        
        Parameters
        ----------
        shape : tuple of ints
            The shape of the data to upload
        format : GL enum
            The format of the texture data. Can be LUMINANCE, LUMINANCE_ALPHA,
            RGB, and RGBA.
        """
        nrows, ncols = self._get_tile_info(shape)
        sim_shape = shape[1] * nrows, shape[2] * ncols
        super().set_size(sim_shape, format)
        
        self.u_shape = shape[0], shape[1], shape[2]  # for uniform
        self.u_tiles = ncols, nrows
    
    def set_data(self, offset, shape, data):
        """Set the 3D texture data.
        
        Parameters
        ----------
        offset : tuple of ints
            Offset in pixels for each dimension.
        shape : tuple of ints
            The shape of the data to upload
        data : typed array
            The actual pixel data. Can be of any type, but on the GPU the
            dat is stored in 8 bit precision.
        """
        if len(shape) == 3:
            shape = shape[0], shape[1], shape[2], 1
        
        if not all([i == 0 for i in offset]):
            raise ValueError('Texture3DLike does not support nonzero offset (for now)')
        # todo: allow nonzero offset
        
        nrows, ncols = self._get_tile_info(shape)
        sim_shape = shape[1] * nrows, shape[2] * ncols, shape[3]

        if ncols == 1:
            # Great, data can stay contiguous
            super().set_data((0, 0), sim_shape, data)
        else:
            # We need to upload the tiles one by one - fill row by row
            # First reset to zeros
            Type = data.constructor  # noqa
            zeros = Type(sim_shape[0] * sim_shape[1] * sim_shape[2])
            super().set_data((0, 0), sim_shape, zeros)
            #
            # todo: check whether its more efficient to first tile a new array and upload in one step
            for z in range(shape[0]):
                row, col = z // ncols, z % ncols
                elements_per_tile = len(data) // shape[0]
                tile = data[z * elements_per_tile:(z + 1) * elements_per_tile]
                super().set_data((row * shape[1], col * shape[2]), shape[1:], tile)


if __name__ == '__main__':
    from flexx.pyscript.functions import script2js
    script2js(__file__, 'gloo2+')  # The + is makes it a UMD module
    
    # AK: a small hack to make it easier for me to devekop this for Bokeh
    import os
    if os.getenv('GLOO2_DEPLOY_BOKEH', ''):
        import bokeh
        bokehdir = os.path.abspath(os.path.join(bokeh.__file__, '..', '..',
                                'bokehjs/src/vendor/gloo/'))
        if os.path.isdir(bokehdir):
            script2js(__file__, 'gloo2+', bokehdir + '/gloo2.js')
