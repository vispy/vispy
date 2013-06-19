# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

import OpenGL.GL as gl
import numpy as np

#from OpenGL.GL.ARB.texture_rg import *
#from OpenGL.raw.GL.ARB.half_float_vertex import *
#from OpenGL.raw.GL.ARB.depth_buffer_float import *

import sys
if sys.version_info > (3,):
    basestring = str
    
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
        """ The handle (i.e. 'name') to the underlying OpenGL object.
        """
        return self._handle



class _RawTexture(GLObject_mixin):
    """ This class demonstrates the minimal encapsulation of an OpenGl
    texture. The rest is mostly sugar and stuff to support deferred
    loading and settings.
    """
    
    def __init__(self, target):
        
        # Store target (i.e. the texture type)
        aliases = {1:gl.GL_TEXTURE_1D, 2:gl.GL_TEXTURE_2D, 3:gl.GL_TEXTURE_3D}
        target = aliases.get(target, target)
        if target not in [gl.GL_TEXTURE_1D, gl.GL_TEXTURE_2D, gl.GL_TEXTURE_3D]:
            raise ValueError('Unsupported target "%r"' % target)
        self._target = target
        
        # Texture ID (by which OpenGl identifies the texture)
        # 0 means uninitialized, <0 means error.
        self._handle = 0
        
        # To store the used texture unit so we can disable it properly.
        self._unit = -1
        self._useUnit = None # todo: set to True if OpenGl version high enough
    
    
    def _create(self):
        self._handle = gl.glGenTextures(1)
    
    def delete(self):
        """ Delete the texture from OpenGl memory.
        Note that the right context should be active when this method is 
        called.
        """
        try:
            if self._handle > 0:
                gl.glDeleteTextures([self._handle])
        except Exception:
            pass
        self._handle = 0
    
    def __del__(self):
        self.delete()
    
    
    def _enable(self, unit=None):
        gl.glEnable(self._target) # todo ... push on some stack? like glPushAttrib
        
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
    
    
    def _test_upload(self, data, internalformat, format, level=0):
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
        args = [target, level, internalformat] + size + [0, format, gltype, None]
        
        # Do fake upload
        uploadFun(*tuple(args))
        
        # Test and return
        ok = gl.glGetTexLevelParameteriv(target, 0, gl.GL_TEXTURE_WIDTH)
        return bool(ok)
    
    
    def _upload(self, data, internalformat, format, level=0):
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
        args = [target, level, internalformat] + size + [0, format, gltype, data]
        
        # Check the alignment of the texture
        alignment = texture_alignment(data.shape[-1])
        if alignment != 4:
            gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, alignment)
        
        # Call
        uploadFun(*tuple(args))
        
        # Check if we need to reset our pixel store state
        if alignment != 4:
            gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 4)
    
    
    def _update(self, data, offset, internalformat, format, level=0):
        """ Update an existing texture object.
        """
        # Determine function and target from texType
        D = {   gl.GL_TEXTURE_1D: (gl.glTexSubImage1D, gl.GL_TEXTURE_1D, 1),
                gl.GL_TEXTURE_2D: (gl.glTexSubImage2D, gl.GL_TEXTURE_2D, 2),
                gl.GL_TEXTURE_3D: (gl.glTexSubImage3D, gl.GL_TEXTURE_3D, 3)}
        uploadFun, target, ndim = D[self._target]
        
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
    
    Parameters
    ----------
    target : gl_enum
        The target of the texture, currently supported are
        GL_TEXTURE_1D, GL_TEXTURE_2D, and GL_TEXTURE_3D.
    allow_downsampling : bool
        Whether to allow downsamling of data if it does not fit in OpenGl
        memory. Intended for compatibility with older systems.
    allow_padding : bool
        Whether to allow the data to be padded to a factor of 2. Intended
        for compatibility with older systems (OpenGL<2.0, and some ATI drivers).
    
    """
    # Builds on the raw texture class by implementing convenience and lazy loading
    
    def __init__(self, target, allow_downsampling=False, allow_padding=False):
        _RawTexture.__init__(self, target)
        
        # A reference (not a weak one) to be able to process defereed
        # (i.e. lazy) loading.
        self._pendingData = None
        
        # The shape of the data as uploaded to OpenGl. Is None if no
        # data was uploaded. Note that the self._shape does not have to 
        # be self._pendingData.shape; the data might be downsampled.
        self._shape = None
        
        # The parameters that apply to this texture. One variable to 
        # keep track of pending parameters, the other for resetting
        # parameters if its re-uploaded.
        self._texture_params = {}
        self._pending_params = {}
        
        # Set default parameters for min and mag filter, otherwise an
        # image is not shown by default, since the default min_filter
        # is GL_NEAREST_MIPMAP_LINEAR
        self.set_parameter('MIN_FILTER', gl.GL_LINEAR)
        self.set_parameter('MAG_FILTER', gl.GL_LINEAR)
        
        # Allow modifying the data? This is mainly to allow images to
        # be displayed (more or less) correctly on older systems. On
        # newer systems, padding and downsampling would generally never
        # be used. 
        self._allow_downsampling = allow_downsampling
        self._allow_padding = allow_padding
    
    
    def set_parameter(self, param, value):
        """ Set texture parameter. The param can be an OpenGL constant 
        or a string that corresponds to such a constant:
        
        GL_DEPTH_STENCIL_TEXTURE_MODE, BASE_LEVEL, BORDER_COLOR,
        COMPARE_FUNC, COMPARE_MODE, LOD_BIAS, MIN_FILTER, MAG_FILTER,
        MIN_LOD, MAX_LOD, MAX_LEVEL, SWIZZLE_R, SWIZZLE_G, SWIZZLE_B,
        SWIZZLE_A, SWIZZLE_RGBA, WRAP_S, WRAP_T, WRAP_R.
        """
        # Allow strings
        if isinstance(param, basestring):
            param = param.upper()
            if not param.startswith('GL'):
                param = 'GL_TEXTURE_' + param
            param = getattr(gl, param)
        # Set 
        self._pending_params[param] = value
        self._texture_params[param] = value
    
    
    def set_data(self, data, offset=None, level=0, internal_format=None, format=None):
        """ Set the data for this texture. This method can be called at any
        time (even if there is no context yet).
        
        If the shape of the given data matches the shape of the current
        texture, the data is updated in a fast manner.
        
        Parameters
        ----------
        data : numpy array
            The texture data to set.
        offset : tuple
            The offset for each dimension, to update part of the texture.
        level : int
            The mipmap level. Default 0.
        internal_format : OpenGL enum
            The internal format representation. If not given, it is
            decuced from the given data.
        format : OpenGL enum
            The format representation of the data. If not given, it is
            decuced from the given data.
        
        """
        # todo: allow setting shape, but without data
        
        # Check data
        if not isinstance(data, np.ndarray):
            raise ValueError("Data should be a numpy array.")
        
        # Reset if there was an error earlier
        if self._handle < 0:
            self._handle = 0
            self._shape = None
        
        # Check offset
        MAP = {gl.GL_TEXTURE_1D:1, gl.GL_TEXTURE_2D:2, gl.GL_TEXTURE_3D:3}
        ndim = MAP.get(self._target, 0)
        if offset is not None:
            offset = [int(i) for i in offset]
            assert len(offset) == len(data.shape[:ndim])
        elif data.shape == self._shape:
            # If data is of same shape as current texture, update is much faster
            offset = [0 for i in self._shape[:ndim]]
        
        # Set pending data ...
        self._pendingData = data, offset, level, internal_format, format
        self._shape = data.shape
    
    
    def _enable(self):
        """ Overloaded _enable method to handle deferred uploading and
        preparing the texture. Does nothing is texture is invalid
        (self._handle < 0).
          * Upload pending data
          * Bind the texture.
        """
        # Error last time
        if self._handle < 0:
            return
        
        # Older OpenGl versions do not know about 3D textures
        # Check is in _enable, because we need an opengl context
        if self._target == gl.GL_TEXTURE_3D and not getOpenGlCapable('1.2','3D textures'):
            self._handle = -1
            return
        
        # Need to update data?
        if self._pendingData:
            pendingData, self._pendingData = self._pendingData, None
            # Process pending data
            self._process_pending_data(*pendingData)
            # If not ok, try padding (if allowed)
            if self._allow_padding and not gl.glIsTexture(self._handle):
                data = make_power_of_two(pendingData[0])
                if data is not pendingData[0]:
                    print("Warning: the data was padded to make it a power of two.")
                self._process_pending_data(data, *pendingData[1:])
            # If not ok, warn (one time)
            if not gl.glIsTexture(self._handle):
                self._handle = -1
                print('Warning enabling texture, the texture is not valid.')
                return
        
        # Is the texture valid? It may simply not have been given data yet
        if self._handle == 0:
            return
        if not gl.glIsTexture(self._handle): 
            raise RuntimeError('This should not happen (texture is invalid)')
        
        # Enable
        _RawTexture._enable(self, 0) # todo: unit
        
        # Need to update any parameters?
        while self._pending_params:
            param, value = self._pending_params.popitem()
            gl.glTexParameter(self._target, param, value)
    
    
    def _process_pending_data(self, data, offset, level, internal_format, format):
        """ Process the pending data. Uploading the data (i.e. create
        a new texture) or updating it (a subsection).
        """
        
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
        
        # Determine format and internalformat (both can be None)
        if None in (internal_format, format):
            internal_format_, format_ = get_format(data.shape, self._target)
            internal_format = internal_format or internal_format_
            format = format or format_
        
        if offset:
            # Update: fast!
            _RawTexture._enable(self)
            if self._handle <= 0 or not gl.glIsTexture(self._handle):
                raise ValueError('Cannot update texture if there is no texture.')
            self._update(data, offset, internal_format, format, level)
            
        else:
            # (re)upload: slower
            # We delete the existing texture first. In theory this
            # should not be necessary, but some implementations cause
            # memory leaks otherwise.
            self.delete() 
            self._create()
            _RawTexture._enable(self)
            # Test whether it fits, downsample if necessary (and allowed)
            for count in range(0,9):
                ok = self._test_upload(data, internal_format, format, level)
                if ok or not self._allow_downsampling:
                    break
                data = downsample(data, self._target)
            if not ok:   
                msg = "Could not upload texture to OpenGL"  
                msg += bool(count) * ("even after %i times downsampling." % count)
                raise MemoryError(msg)
            elif count:
                print("Warning: data was downscaled %i times." % count)
            # Upload!
            self._upload(data, internal_format, format, level)
            # Set all parameters that the user set
            for param, value in self._texture_params.items():
               gl.glTexParameter(self._target, param, value)
            self._pending_params = {} # We just applied all 
            # If all is well, the _handle, should now be a valid texture



class Texture1D(Texture):
    """ Representation of a 1D texture.
    
    Parameters
    ----------
    allow_downsampling : bool
        Whether to allow downsamling of data if it does not fit in OpenGl
        memory. Intended for compatibility with older systems. Default False.
    allow_padding : bool
        Whether to allow the data to be padded to a factor of 2.
        Intended for compatibility with older systems (OpenGL<2.0, and
        some ATI drivers). Default False.
    
    """
    def __init__(self):
        Texture.__init__(self, gl.GL_TEXTURE_1D, *args, **kwargs)



class Texture2D(Texture):
    """ Representation of a 2D texture.
    
    Parameters
    ----------
    allow_downsampling : bool
        Whether to allow downsamling of data if it does not fit in OpenGl
        memory. Intended for compatibility with older systems. Default False.
    allow_padding : bool
        Whether to allow the data to be padded to a factor of 2.
        Intended for compatibility with older systems (OpenGL<2.0, and
        some ATI drivers). Default False.
    
    """
    def __init__(self, *args, **kwargs):
        Texture.__init__(self, gl.GL_TEXTURE_2D, *args, **kwargs)



class Texture3D(Texture):
    """ Representation of a 3D texture.
    
    Parameters
    ----------
    allow_downsampling : bool
        Whether to allow downsamling of data if it does not fit in OpenGl
        memory. Intended for compatibility with older systems. Default False.
    allow_padding : bool
        Whether to allow the data to be padded to a factor of 2.
        Intended for compatibility with older systems (OpenGL<2.0, and
        some ATI drivers). Default False.
    
    """
    def __init__(self, allow_downsampling=False):
        Texture.__init__(self, gl.GL_TEXTURE_3D, *args, **kwargs)


## Utilities


def get_format(shape, target):
    """ Get internalformat and format, based on the target
    and the shape. If the shape does not match with the texture
    type, an exception is raised.
    """
    
    if target == gl.GL_TEXTURE_1D:
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
    
    elif target == gl.GL_TEXTURE_2D:
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
    
    elif target == gl.GL_TEXTURE_3D:
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


def make_power_of_two(data, ndim):
    """ If necessary, pad the data with zeros, to make the shape 
    a power of two. If it already is shaped ok, the original data
    is returned.
    
    Use this function for systems with OpenGl < 2.0. 
    
    Note: In theory, getOpenGlCapable('2.0') should be enough to
    determine if padding is required. However, bloody ATI drivers
    sometimes need 2**n textures even if OpenGl > 2.0. (I've 
    encountered this with someones PC and verified that an approach similar
    to the one in this module (from visvis) produces correct results.)
    """
    def nearestN(n1):
        n2 = 2
        while n2 < n1:
            n2*=2
        return n2
    
    # get old and new shape
    s1 = [n for n in data.shape]
    s2 = [nearestN(n) for n in data.shape]
    s2[ndim:] = s1[ndim:] # for color images    
    
    # if not required return original
    if s1 == s2:
        return data
    
    # create empty image
    data2 = np.zeros(s2,dtype=data.dtype)
    
    # fill in the original data
    if ndim==1:
        data2[:s1[0]] = data
    elif ndim==2:
        data2[:s1[0],:s1[1]] = data
    elif ndim==3:
        data2[:s1[0],:s1[1],:s1[2]] = data
    else:
        raise ValueError("Cannot pad data of this dimension.")
    return data2


def downsample(data, target):
    """ Downsample the data. Peforming a simple form of smoothing to prevent
    aliasing. 
    
    """
    
    if target==gl.GL_TEXTURE_1D:
        # Decimate
        data2 = data[::2] * 0.4
        # Average in x
        tmp = data[1::2] * 0.3
        data2[:tmp.shape[0]] += tmp
        data2[1:] += tmp[:data2.shape[0]-1]
    elif target==gl.GL_TEXTURE_2D:
        # Decimate
        data2 = data[::2,::2] * 0.4
        # Average in y
        tmp = data[1::2,::2] * 0.15
        data2[:tmp.shape[0],:] += tmp
        data2[1:,:] += tmp[:data2.shape[0]-1,:]
        # Average in x
        tmp = data[::2,1::2] * 0.15
        data2[:,:tmp.shape[1]] += tmp
        data2[:,1:] += tmp[:,:data2.shape[1]-1]
    elif target==gl.GL_TEXTURE_3D:
        # Decimate
        data2 = data[::2,::2,::2] * 0.4
        # Average in z
        tmp = data[1::2,::2,::2] * 0.1
        data2[:tmp.shape[0],:,:] += tmp
        data2[1:,:,:] += tmp[:data2.shape[0]-1,:,:]
        # Average in y
        tmp = data[::2,1::2,::2] * 0.1
        data2[:,:tmp.shape[1],:] += tmp
        data2[:,1:,:] += tmp[:,:data2.shape[1]-1,:]
        # Average in x
        tmp = data[::2,::2,1::2] * 0.1
        data2[:,:,:tmp.shape[2]] += tmp
        data2[:,:,1:] += tmp[:,:,:data2.shape[2]-1]
    else:
        raise ValueError("Cannot downsample data of this dimension.")
    return data2


# from pylgy
def texture_alignment(width):
    """Determines a textures byte alignment.

    If the width isn't a power of 2
    we need to adjust the byte alignment of the image.
    The image height is unimportant

    http://www.opengl.org/wiki/Common_Mistakes#Texture_upload_and_pixel_reads
    """
    
    # we know the alignment is appropriate
    # if we can divide the width by the
    # alignment cleanly
    # valid alignments are 1,2,4 and 8
    # put 4 first, since it's the default
    alignments = [4,8,2,1]
    for alignment in alignments:
        if width % alignment == 0:
            return alignment