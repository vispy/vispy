
import OpenGL.GL as gl

#from OpenGL.GL.ARB.texture_rg import *
#from OpenGL.raw.GL.ARB.half_float_vertex import *
#from OpenGL.raw.GL.ARB.depth_buffer_float import *

def getOpenGlCapable(version, description):
    return True # todo: we need something like this


# todo: rename _enable/_disable to _bind/_unbind



# Dict that maps numpy datatypes to openGL data types
DTYPES = {  'uint8':gl.GL_UNSIGNED_BYTE,    'int8':gl.GL_BYTE,
            'uint16':gl.GL_UNSIGNED_SHORT,  'int16':gl.GL_SHORT, 
            'uint32':gl.GL_UNSIGNED_INT,    'int32':gl.GL_INT, 
            'float32':gl.GL_FLOAT }
            # todo: GL_DOUBLE available from what version?


class GLObject_mixin(object):
    
    def __enter__(self):
        self._enable()
        return self
    
    def __exit__(self, type, value, traceback):
        self._disable()
    
    @property
    def handle(self):
        return self._handle



class _RawTexture(GLObject_mixin):
    """ This class demonstrates the minimal encapsulation
    of an OpenGl texture. The rest is all sugar.
    """
    
    def __init__(self, target):
        
        # Store target (i.e. the texture type)
        target = {1:gl.GL_TEXTURE_1D, 2:gl.GL_TEXTURE_2D, 3:gl.GL_TEXTURE_3D}
        if target not in [gl.GL_TEXTURE_1D, gl.GL_TEXTURE_2D, gl.GL_TEXTURE_3D]:
            raise ValueError('Unsupported target "%r"' % target)
        self._target = target
        
        # Get number of dimensions of the data
        self._ndim = {gl.GL_TEXTURE_1D:1, gl.GL_TEXTURE_2D:2, 
                        gl.GL_TEXTURE_3D:3}.get(target, None)
        
        # Texture ID (by which OpenGl identifies the texture)
        self._handle = 0
        
        # To store the used texture unit so we can disable it properly.
        self._unit = -1
        self._useUnit = None # set to True if OpenGl version high enough
    
    
    def _create(self):
        self._handle = gl.glGenTextures(1)
    
    
    def _delete(self):
        try:
            if self._handle > 0:
                gl.glDeleteTextures([self._handle])
        except Exception:
            pass
        self._handle = 0
    
    def __del__(self):
        self._delete()
    
    
    def _enable(self, unit=None):
        gl.glEnable(self._target) # todo ... push on some stack?
        
        if unit is not None:
            # Store texture-unit-id, and activate.
            self._useUnit = unit
            if self._useUnit is None:
                self._useUnit = getOpenGlCapable('1.3')        
            if self._useUnit:
                gl.glActiveTexture(gl.GL_TEXTURE0 + unit)  # Opengl v1.3
        
        # Bind
        gl.glBindTexture(self._target, self._handle)
    
    
    def _disable(self):
        # Select active texture if we can
        if self._unit >= 0 and self._useUnit:
            gl.glActiveTexture(gl.GL_TEXTURE0 + self._unit)
            self._unit = -1
        # Unbind and disable
        gl.glBindTexture(self._target, 0)
        # Set active texture unit to default (0)
        if self._useUnit:
            gl.glActiveTexture(gl.GL_TEXTURE0)
        
         gl.glDisable(self._target)
    
    
    def _test_upload(self, data, internalformat, format, level=0, border=False):
        """ Test whether we can create a texture of the given shape.
        Returns True if we can, False if we can't.
        """
        # Determine function and proxy-target from self._target
        D = {   gl.GL_TEXTURE_1D: (gl.glTexImage1D, gl.GL_PROXY_TEXTURE_1D, 1),
                gl.GL_TEXTURE_2D: (gl.glTexImage2D, gl.GL_PROXY_TEXTURE_2D, 2),
                gl.GL_TEXTURE_3D: (gl.glTexImage3D, gl.GL_PROXY_TEXTURE_3D, 3)}
        uploadFun, target, ndim = D[self._target]
        
        # Build args list
        size, gltype = self._get_size_and_type(data, ndim)
        args = [target, level, internalformat] + size + [border, format, gltype, None]
        
        # Do fake upload
        uploadFun(*tuple(args))
        
        # Test and return
        ok = gl.glGetTexLevelParameteriv(target, 0, gl.GL_TEXTURE_WIDTH)
        return bool(ok)
    
    
    def _upload(self, data, internalformat, format, level=0, border=False):
        """ Upload a texture to the current texture object. 
        It should have been verified that the texture will fit.
        """
        # Determine function and target from texType
        D = {   gl.GL_TEXTURE_1D: (gl.glTexImage1D, gl.GL_TEXTURE_1D, 1),
                gl.GL_TEXTURE_2D: (gl.glTexImage2D, gl.GL_TEXTURE_2D, 2),
                gl.GL_TEXTURE_3D: (gl.glTexImage3D, gl.GL_TEXTURE_3D, 3)}
        uploadFun, target, ndim = D[self._target]
        
        # Determine type
        thetype = data.dtype.name
        if not thetype in DTYPES: # Note that we convert if necessary in Texture
            raise ValueError("Cannot convert datatype %s." % thetype)
        gltype = DTYPES[thetype]
        
        # Build args list
        size, gltype = self._get_size_and_type(data, ndim)
        args = [target, level, internalformat] + size + [border, format, gltype, data]
        
        # Call
        uploadFun(*tuple(args))
    
    
    def _update(self, data, offset, internalformat, format, level=0):
        """ Update an existing texture object.
        """
        # Determine function and target from texType
        D = {   gl.GL_TEXTURE_1D: (gl.glTexSubImage1D, gl.GL_TEXTURE_1D, 1),
                gl.GL_TEXTURE_2D: (gl.glTexSubImage2D, gl.GL_TEXTURE_2D, 2),
                gl.GL_TEXTURE_3D: (gl.glTexSubImage3D, gl.GL_TEXTURE_3D, 3)}
        uploadFun, target, ndim = D[self._ndim]
        
        # Build argument list
        size, gltype = self._get_size_and_type(data, ndim)
        offset = [i for i in offset]
        assert len(offset) == len(size)
        args = [target, level] + offset + size + [format, gltype, data]
        
        # Upload!
        uploadFun(*tuple(args))
    
    
    def _get_size_and_type(self, data, ndim):
        # Determine size
        size = [i for i in reversed( data.shape[:ndim] )]
        # Determine type
        thetype = data.dtype.name
        if not thetype in DTYPES: # Note that we convert if necessary in Texture
            raise ValueError("Cannot convert datatype %s." % thetype)
        gltype = DTYPES[thetype]
        # Done
        return size, gltype



class Texture(_RawTexture):
    """ The base texture class. 
    """
    # Builds on the raw texture class by implementing convenience and lazy loading
    
    def __init__(self, target):
        _RawTexture.__init__(self, target)
        
        # A reference (not a weak one) to be able to process defereed
        # (i.e. lazy) loading.
        self._pendingData = None
        
        # The shape of the data as uploaded to OpenGl. Is None if no
        # data was uploaded. Note that the self._shape does not have to 
        # be self._pendingData.shape; the data might be downsampled.
        self._shape = None
    
    
    def set_data(self, data, offset=None, level=0, border=False,
            internal_format=None, format=None):
        
        # Check data
        if not isinstance(data, np.ndarray):
            raise ValueError("Data should be a numpy array.")
        
        # Check offset
        MAP = [gl.GL_TEXTURE_1D:1, gl.GL_TEXTURE_2D:2, gl.GL_TEXTURE_3D:3]
        ndim = MAP.get(self._target, 0)
        if offset is not None:
            offset = [int(i) for i in offset]
            assert len(offset) == len(data.shape[:ndim])
        elif data.shape == self._shape:
            # If data is of same shape, we can update it much faster
            offset = [0 for i in self._shape[:ndim]]
        
        # Convert data type to one supported by OpenGL
        if data.dtype.name not in DTYPES:
            # Long integers become floats; int32 would not have enough range
            if data.dtype in (np.int64, np.uint64):
                data = data.astype(np.float32)
            # Bools become bytes
            elif data.dtype == np.bool:
                data = data.astype(np.uint8)
            else:
                # Make singles in all other cases (e.g. np.float64, np.float128)
                # We cannot explicitly use float128, since its not always defined
                data = data.astype(np.float32)
        
        # Determine format and internalformat
        if None in (internalformat, format):
            internal_format_, format_ = self._get_format(data.shape)
            internal_format = internal_format or internal_format_
            format = format or format_
        
        # Set pending data ...
        self._pendingData = data, offset, level, border, internal_format, format
        self._shape = data.shape
    
    
    def _enable(self):
        
        # todo: Have a proper look at how to deal with errors etc. 
        # like preventing from printing warnings on each draw, but also
        # allow recovering.
        
        # Error last time
        if self._handle < 0:
            return
        
        # Older OpenGl versions do not know about 3D textures
        if self._target == gl.GL_TEXTURE_3D and not getOpenGlCapable('1.2','3D textures'):
            self._handle = -1
            return
        
        # Was this all?
        if not self._pendingData:
            self._enable(self) # todo: unit
        
        # else -> pending data
        
        # Get data
        data, offset, level, border, internal_format, format = self._pendingData
        self._pendingData = None
        
        # Bind (so we can upload)
        self._enable(self)
        
        if offset:
            # Update: fast!
            if self._handle <= 0 or not gl.glIsTexture(self._handle):
                raise ValueError('Cannot update texture if there is no texture.')
            self._update(data, offset, internal_format, format, level, border)
            
        else:
            # (re)upload, do more checking!
            self._delete() 
            self._create()
            # todo: need padding?  -> in Image class, but we need to signal
            # todo: downsampling?  -> in Image class, but we need to signal
            # Test and upload
            ok = self._test_upload(data, offset, internal_format, format, level)
            if not ok:
                raise ValueError('Could not upload texture.')
            self._upload(data, offset, internal_format, format, level, border)
        
        # Enable
        self._enable(self) # todo: unit
    
    
    def _get_format(self, shape):
        """ Get internalformat and format, based on the self._target
        and the shape. If the shape does not match with the texture
        type, an exception is raised.
        """
        
        if self._target == gl.GL_TEXTURE_1D:
            if len(shape)==1:
                iformat, format = gl.GL_LUMINANCE8, gl.GL_LUMINANCE
            elif len(shape)==2 and shape[1] == 1:
                iformat, format = gl.GL_LUMINANCE8, gl.GL_LUMINANCE
            elif len(shape)==2 and shape[1] == 3:
                iformat, format = gl.GL_RGB, gl.GL_RGB
            elif len(shape)==2 and shape[1] == 4:
                iformat, format = gl.GL_RGBA, gl.GL_RGBA
            else:
                raise ValueError("Cannot determine format: data of invalid shape.")
        
        elif self._ndim == gl.GL_TEXTURE_2D:
            if len(shape)==2:
                iformat, format = gl.GL_LUMINANCE8, gl.GL_LUMINANCE                
            elif len(shape)==3 and shape[2]==1:
                iformat, format = gl.GL_LUMINANCE8, gl.GL_LUMINANCE
            elif len(shape)==3 and shape[2]==3:
                iformat, format = gl.GL_RGB, gl.GL_RGB
            elif len(shape)==3 and shape[2]==4:
                iformat, format = gl.GL_RGBA, gl.GL_RGBA
            else:
                raise ValueError("Cannot determine format: data of invalid shape.")
        
        elif self._ndim == gl.GL_TEXTURE_3D:
            if len(shape)==3:
                iformat, format = gl.GL_LUMINANCE8, gl.GL_LUMINANCE
            elif len(shape)==4 and shape[3]==1:
                iformat, format = gl.GL_LUMINANCE8, gl.GL_LUMINANCE
            elif len(shape)==4 and shape[3]==3:
                iformat, format = gl.GL_RGB, gl.GL_RGB
            elif len(shape)==4 and shape[3]==4:
                iformat, format = gl.GL_RGBA, gl.GL_RGBA
            else:
                raise ValueError("Cannot determine format: data of invalid shape.")
        
        else:
            raise ValueError("Cannot determine format with these dimensions.")
        
        return iformat, format


class Texture1D(Texture):
    pass

class Texture2D(Texture):
    pass

class Texture3D(Texture):
    pass
    