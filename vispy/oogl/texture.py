# -*- coding: utf-8 -*-
""" Definition of Texture class.

This code is inspired by similar classes from Visvis and Pygly.

"""

# todo: implement ext_available
# todo: allow setting empty texture (shape, but without data)
# todo: functionality to control scale and bias of pixel values.
# todo: make a Texture1D that makes a nicer interface to a 2D texture
# todo: same for Texture3D?
 

from __future__ import print_function, division, absolute_import

import sys
import numpy as np

from vispy import gl
from . import GLObject, push_enable, pop_enable, ext_available

if sys.version_info > (3,):
    basestring = str


# Dict that maps numpy datatypes to openGL data types
DTYPES = {  'uint8':gl.GL_UNSIGNED_BYTE,    'int8':gl.GL_BYTE,
            'uint16':gl.GL_UNSIGNED_SHORT,  'int16':gl.GL_SHORT, 
            'uint32':gl.GL_UNSIGNED_INT,    'int32':gl.GL_INT, 
            'float32':gl.GL_FLOAT }
            # gl.GL_DOUBLE?


class _RawTexture(GLObject):
    """ This class demonstrates the minimal encapsulation of an OpenGl
    texture. The rest is mostly sugar and stuff to support deferred
    loading and settings.
    """
    
    def __init__(self, target):
        
        # Store target (i.e. the texture type)
        if target not in [gl.GL_TEXTURE_2D, gl.ext.GL_TEXTURE_3D]:
            raise ValueError('Unsupported target "%r"' % target)
        self._target = target
        
        # Texture ID (by which OpenGl identifies the texture)
        # 0 means uninitialized, <0 means error.
        self._handle = 0
        
        # To store the used texture unit so we can disable it properly.
        self._unit = -1
    
    
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
    
    
    def _enable(self):
        """ To be called by context handler. Never call this yourself.
        """
        # Enable things that we need
        push_enable(self._target)
        # Set active texture unit
        if self._unit >= 0:
            gl.glActiveTexture(gl.GL_TEXTURE0 + self._unit)
        # Bind
        gl.glBindTexture(self._target, self._handle)
    
    
    def _disable(self):
        """ To be called by context handler. Never call this yourself.
        """
        # Select active texture if we can
        if self._unit >= 0:
            gl.glActiveTexture(gl.GL_TEXTURE0 + self._unit)
            self._unit = -1
        # Unbind and disable
        gl.glBindTexture(self._target, 0)
        # Set active texture unit to default (0)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        # No need for texturing anymore
        pop_enable(self._target)
    
    
    def _upload(self, data, internalformat, format, level=0):
        """ Upload a texture to the current texture object. 
        It should have been verified that the texture will fit.
        """
        # Determine function and target from texType
        D = {   #gl.GL_TEXTURE_1D: (gl.glTexImage1D, 1),
                gl.GL_TEXTURE_2D: (gl.glTexImage2D, 2),
                gl.ext.GL_TEXTURE_3D: (gl.ext.glTexImage3D, 3)}
        uploadFun, ndim = D[self._target]
        
        # Determine type
        thetype = data.dtype.name
        if not thetype in DTYPES: # Note that we convert if necessary in Texture
            raise ValueError("Cannot convert datatype %s." % thetype)
        gltype = DTYPES[thetype]
        
        # Build args list
        size, gltype = self._get_size_and_type(data, ndim)
        args = [self._target, level, internalformat] + size + [0, format, gltype, data]
        
        # Check the alignment of the texture
        alignment = self._get_alignment(data.shape[-1])
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
        D = {   #gl.GL_TEXTURE_1D: (gl.glTexSubImage1D, 1),
                gl.GL_TEXTURE_2D: (gl.glTexSubImage2D, 2),
                gl.ext.GL_TEXTURE_3D: (gl.ext.glTexSubImage3D, 3)}
        uploadFun, ndim = D[self._target]
        
        # Build argument list
        size, gltype = self._get_size_and_type(data, ndim)
        offset = [i for i in offset]
        assert len(offset) == len(size)
        args = [self._target, level] + offset + size + [format, gltype, data]
        
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
    
    # from pylgy
    def _get_alignment(self, width):
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



class Texture(_RawTexture):
    """ Representation of an OpenGL texture. This class is designed to
    allow setting data and parameters at any time; the actual uploading
    of data and applying of parameters is deferred until the texture
    is enabled (which will in general be right before it is used during
    drawing). The exceptions are the delete method and using this class
    as a context manager. In these cases the caller needs to make sure 
    that the right OpenGL context is current.
    
    To bind/enable the texture, use it as a context manager. An object
    of this class can be called with one (integer) argument to set the
    texture unit. This can be combined in ``with tex(0): ...``.
    
    Parameters
    ----------
    target : gl_enum
        The target of the texture, OpenGL ES 2.0 allows 
        GL_TEXTURE_2D and GL_TEXTURE_3D (needs extension).
    
    """
    # Builds on the raw texture class by implementing convenience and lazy loading
    
    def __init__(self, target):
        _RawTexture.__init__(self, target)
        
        # A reference (not a weak one) to be able to process deferred
        # (i.e. lazy) loading. Also store the shape.
        self._pending_data = None
        self._texture_shape = None
        
        # The parameters that apply to this texture. One variable to 
        # keep track of pending parameters, the other for resetting
        # parameters if its re-uploaded.
        self._texture_params = {}
        self._pending_params = {}
        
        # Set default parameters for min and mag filter, otherwise an
        # image is not shown by default, since the default min_filter
        # is GL_NEAREST_MIPMAP_LINEAR
        self.set_parameter(gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        self.set_parameter(gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    
    
    def __call__(self, unit):
        """ Calling a texture sets the texture unit.
        """
        self._unit = int(unit)
        return self
    
    
    def set_parameter(self, param, value):
        """ Set texture parameter, can be called at any time. The param
        can be an OpenGL constant or a string that corresponds to such
        a constant. OpenGL ES 2.0 allows the following parameters:
        GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_TEXTURE_WRAP_S,
        TEXTURE_WRAP_T, GL_TEXTURE_WRAP_R (with extension).
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
        
        # Check data
        if not isinstance(data, np.ndarray):
            raise ValueError("Data should be a numpy array.")
        
        # Reset if there was an error earlier
        if self._handle < 0:
            self._handle = 0
            self._texture_shape = None
        
        # Check offset
        MAP = {gl.GL_TEXTURE_2D:2, gl.ext.GL_TEXTURE_3D:3}
        ndim = MAP.get(self._target, 0)
        if offset is not None:
            offset = [int(i) for i in offset]
            assert len(offset) == len(data.shape[:ndim])
        elif data.shape == self._texture_shape:
            # If data is of same shape as current texture, update is much faster
            offset = [0 for i in self._texture_shape[:ndim]]
        
        # Set pending data ...
        self._pending_data = data, offset, level, internal_format, format
        self._texture_shape = data.shape
    
    
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
        
        # If we use a 3D texture, we need an extension
        if self._target == gl.ext.GL_TEXTURE_3D:
            if not ext_available('GL_texture_3D'):
                self._handle = -1
                return
        
        # Need to update data?
        if self._pending_data:
            pendingData, self._pending_data = self._pending_data, None
            # Process pending data
            self._process_pending_data(*pendingData)
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
        _RawTexture._enable(self)
        
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
            gl.glBindTexture(self._target, self._handle)
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
            gl.glBindTexture(self._target, self._handle)
            # Upload!
            self._upload(data, internal_format, format, level)
            # Set all parameters that the user set
            for param, value in self._texture_params.items():
               gl.glTexParameter(self._target, param, value)
            self._pending_params = {} # We just applied all 
            # If all is well, the _handle, should now be a valid texture



class Texture2D(Texture):
    """ Representation of a 2D texture.
    """
    def __init__(self):
        Texture.__init__(self, gl.GL_TEXTURE_2D)



class Texture3D(Texture):
    """ Representation of a 3D texture. Note that for this the
    GL_texture_3D extension needs to be available.
    """
    def __init__(self):
        Texture.__init__(self, gl.ext.GL_TEXTURE_3D)


## Utility functions


def get_format(shape, target):
    """ Get internalformat and format, based on the target
    and the shape. If the shape does not match with the texture
    type, an exception is raised.
    """
    
    if target == 'dummy, just so we can leave the code here':
        if len(shape)==1:
            iformat, format = gl.GL_LUMINANCE, gl.GL_LUMINANCE
        elif len(shape)==2 and shape[1] == 1:
            iformat, format = gl.GL_LUMINANCE, gl.GL_LUMINANCE
        elif len(shape)==2 and shape[1] == 3:
            iformat, format = gl.GL_RGB, gl.GL_RGB
        elif len(shape)==2 and shape[1] == 4:
            iformat, format = gl.GL_RGBA, gl.GL_RGBA
        else:
            raise ValueError("Cannot determine format: data of invalid shape.")
    
    elif target == gl.GL_TEXTURE_2D:
        if len(shape)==2:
            iformat, format = gl.GL_LUMINANCE, gl.GL_LUMINANCE                
        elif len(shape)==3 and shape[2]==1:
            iformat, format = gl.GL_LUMINANCE, gl.GL_LUMINANCE
        elif len(shape)==3 and shape[2]==3:
            iformat, format = gl.GL_RGB, gl.GL_RGB
        elif len(shape)==3 and shape[2]==4:
            iformat, format = gl.GL_RGBA, gl.GL_RGBA
        else:
            raise ValueError("Cannot determine format: data of invalid shape.")
    
    elif target == gl.ext.GL_TEXTURE_3D:
        if len(shape)==3:
            iformat, format = gl.GL_LUMINANCE, gl.GL_LUMINANCE
        elif len(shape)==4 and shape[3]==1:
            iformat, format = gl.GL_LUMINANCE, gl.GL_LUMINANCE
        elif len(shape)==4 and shape[3]==3:
            iformat, format = gl.GL_RGB, gl.GL_RGB
        elif len(shape)==4 and shape[3]==4:
            iformat, format = gl.GL_RGBA, gl.GL_RGBA
        else:
            raise ValueError("Cannot determine format: data of invalid shape.")
    
    else:
        raise ValueError("Cannot determine format with these dimensions.")
    
    return iformat, format

