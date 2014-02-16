# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Definition of Texture class.

This code is inspired by similar classes from Visvis and Pygly.

"""

# todo: implement ext_available
# todo: make a Texture1D that makes a nicer interface to a 2D texture
# todo: same for Texture3D?
# todo: Cubemap texture
# todo: mipmapping, allow creating mipmaps
# todo: compressed textures?


from __future__ import division

import numpy as np

from . import gl
from . import GLObject, ext_available, convert_to_enum
from ..util import logger


class TextureError(RuntimeError):

    """ Raised when something goes wrong that depens on state that was set
    earlier (due to deferred loading).
    """
    pass


class TextureLevel(object):

    """ Minimal class to hold together some values that together
    represent one texture level.
    """

    def __init__(self, level):
        self.level = level  # 0, 1, 2, etc.
        self.format = None  # GL_RGB, GL_LUMINANCE etc.
        self.shape = None  # Shape of a corresponding numpy array, zyx-order
        self.need_resize = False  # Whether shape or format has changed
        self.pending_data = []  # Data to upload

    def set(self, shape, format):
        """ Set shape and format. Return True if this requires a resize.
        """
        # Discart pending data
        self.pending_data = []
        # If nothing changed, early exit. Otherwise we need a resize
        if (self.shape == shape) and (self.format == format):
            return False
        else:
            self.shape = shape
            self.format = format
            self.need_resize = True
            return True


class Texture(GLObject):

    """ Representation of an OpenGL texture.

    """

    # Dict that maps numpy datatypes to openGL ES 2.0 data types
    # We use strings to be more failsafe; e.g. np.float128 does not always
    # exist
    DTYPE2GTYPE = {'uint8': gl.GL_UNSIGNED_BYTE,
                   # Needs GL_OES_texture_half_float:
                   'float16': gl.ext.GL_HALF_FLOAT,
                   # Needs GL_OES_texture_float:
                   'float32': gl.GL_FLOAT,
                   }

    def __init__(self, target, data=None, format=None, clim=None):
        GLObject.__init__(self)

        # Store target (i.e. the texture type)
        if target not in [gl.GL_TEXTURE_2D, gl.ext.GL_TEXTURE_3D]:
            raise ValueError('Unsupported target "%r"' % target)
        self._target = target

        # Keep track of levels: dict of TextureLevel instances
        # Each texLevel stores shape, format, pending data, need_resize
        self._levels = {}

        # The parameters that apply to this texture. One variable to
        # keep track of pending parameters, the other for resetting
        # parameters if its re-uploaded.
        self._texture_params = {}
        self._pending_params = {}

        # Set default parameters for min and mag filter, otherwise an
        # image is not shown by default, since the default min_filter
        # is GL_NEAREST_MIPMAP_LINEAR
        # Note that mipmapping is not allowed unless the texture_npot
        # extension is available.
        self.set_filter(gl.GL_LINEAR, gl.GL_LINEAR)

        # Set default parameter for clamping. CLAMP_TO_EDGE since that
        # is required if a texture is used as a render target.
        # Also, in OpenGL ES 2.0, wrapping must be CLAMP_TO_EDGE if
        # textures are not a power of two, unless the texture_npot extension
        # is available.
        if self._target == gl.ext.GL_TEXTURE_3D:
            self.set_wrapping(gl.GL_CLAMP_TO_EDGE, gl.GL_CLAMP_TO_EDGE,
                              gl.GL_CLAMP_TO_EDGE)
        else:
            self.set_wrapping(gl.GL_CLAMP_TO_EDGE, gl.GL_CLAMP_TO_EDGE)

        # Reset status; set_filter and set_wrapping were called.
        self._need_update = False

        # Set data?
        if data is None:
            pass
        elif isinstance(data, np.ndarray):
            self.set_data(data, format=format, clim=clim)
        elif isinstance(data, tuple):
            self.set_shape(data, format=format)
        else:
            raise ValueError('Invalid value to initialize Texture with.')

    def set_filter(self, mag_filter, min_filter):
        """ Set interpolation filters. EIther parameter can be None to
        not (re)set it.

        Parameters
        ----------
        mag_filter : str
            The magnification filter (when texels are larger than screen
            pixels). Can be NEAREST, LINEAR. The OpenGL enum can also be given.
        min_filter : str
            The minification filter (when texels are smaller than screen
            pixels). For this filter, mipmapping can be applied to perform
            antialiasing (if mipmaps are available for this texture).
            Can be NEAREST, LINEAR, NEAREST_MIPMAP_NEAREST,
            NEAREST_MIPMAP_LINEAR, LINEAR_MIPMAP_NEAREST,
            LINEAR_MIPMAP_LINEAR. The OpenGL enum can also be given.
        """
        # Allow strings
        mag_filter = convert_to_enum(mag_filter, True)
        min_filter = convert_to_enum(min_filter, True)
        # Check
        assert mag_filter in (None, gl.GL_NEAREST, gl.GL_LINEAR)
        assert min_filter in (
            None,
            gl.GL_NEAREST,
            gl.GL_LINEAR,
            gl.GL_NEAREST_MIPMAP_NEAREST,
            gl.GL_NEAREST_MIPMAP_LINEAR,
            gl.GL_LINEAR_MIPMAP_NEAREST,
            gl.GL_LINEAR_MIPMAP_LINEAR)

        # Set
        if mag_filter is not None:
            self._pending_params[gl.GL_TEXTURE_MAG_FILTER] = mag_filter
            self._texture_params[gl.GL_TEXTURE_MAG_FILTER] = mag_filter
        if min_filter is not None:
            self._pending_params[gl.GL_TEXTURE_MIN_FILTER] = min_filter
            self._texture_params[gl.GL_TEXTURE_MIN_FILTER] = min_filter

        self._need_update = True

    def set_wrapping(self, wrapx, wrapy, wrapz=None):
        """ Set texture coordinate wrapping.

        Parameters
        ----------
        wrapx : str
            The wrapping mode in the x-direction. Can be GL_REPEAT,
            GL_CLAMP_TO_EDGE, GL_MIRRORED_REPEAT. The OpenGL enum can also
            be given.
        wrapy : str
            Dito for y.
        wrapz : str
            Dito for z. Only makes sense for 3D textures, and requires
            the texture_3d extension. Optional.
        """
        # Allow strings
        wrapx = convert_to_enum(wrapx, True)
        wrapy = convert_to_enum(wrapy, True)
        wrapz = convert_to_enum(wrapz, True)
        # Check
        assert wrapx in (
            None,
            gl.GL_REPEAT,
            gl.GL_CLAMP_TO_EDGE,
            gl.GL_MIRRORED_REPEAT)
        assert wrapy in (
            None,
            gl.GL_REPEAT,
            gl.GL_CLAMP_TO_EDGE,
            gl.GL_MIRRORED_REPEAT)
        assert wrapz in (
            None,
            gl.GL_REPEAT,
            gl.GL_CLAMP_TO_EDGE,
            gl.GL_MIRRORED_REPEAT)

        # Set
        if wrapx is not None:
            self._pending_params[gl.GL_TEXTURE_WRAP_S] = wrapx
            self._texture_params[gl.GL_TEXTURE_WRAP_S] = wrapx
        if wrapy is not None:
            self._pending_params[gl.GL_TEXTURE_WRAP_T] = wrapy
            self._texture_params[gl.GL_TEXTURE_WRAP_T] = wrapy
        if wrapz is not None:
            self._pending_params[gl.ext.GL_TEXTURE_WRAP_R] = wrapz
            self._texture_params[gl.ext.GL_TEXTURE_WRAP_R] = wrapz

        self._need_update = True

    def set_shape(self, shape, level=0, format=None):
        """ Allocate storage for this texture. This is useful if the texture
        is used as a render target for an FBO.

        A call that only uses the shape argument does not result in an
        action if the call would not change the shape.

        Parameters
        ----------
        shape : tuple
            The shape of the "virtual" data. By specifying e.g. (20,20,3) for
            a Texture2D, one implicitly sets the format to GL_RGB. Note
            that shape[0] is height.
        level : int
            The mipmap level. Default 0.
        format : str
            The format representation of the data. If not given or None,
            it is decuced from the given data. Can be RGB, RGBA, LUMINANCE,
            LUMINANCE_ALPHA, ALPHA. The OpenGL enum can also be given.
        """

        # Check level, get texLevel instance
        assert isinstance(level, int) and level >= 0
        texLevel = self._levels.get(level, None)
        if texLevel is None:
            texLevel = self._levels[level] = TextureLevel(level)

        # Get ndim
        MAP = {gl.GL_TEXTURE_2D: 2, gl.ext.GL_TEXTURE_3D: 3}
        ndim = MAP.get(self._target, 0)

        # Check shape
        shape = tuple([int(i) for i in shape])
        if not len(shape) in (ndim, ndim + 1):
            raise ValueError('Shape must be ndim or ndim+1.')
        if not all([i > 0 for i in shape]):
            raise ValueError('Shape cannot contain elements <= 0.')

        # Check format
        if format is None:
            format = get_formats(shape, self._target)[0]
        else:
            format = convert_to_enum(format)
            if format not in get_formats(shape, self._target):
                raise ValueError('Given format does not match with shape.')

        # Set new shape and format, force new update if necessary
        self._need_update = texLevel.set(shape, format)

    def set_data(self, data, level=0, format=None, clim=None):
        """ Set the data for this texture. This method can be called at any
        time (even if there is no context yet).

        It is relatively cheap to call this function multiple times,
        only the last data is set right before drawing. If the shape
        of the given data matches the shape of the current texture, the
        data is updated in a fast manner.

        Parameters
        ----------
        data : numpy array
            The texture data to set.
        level : int
            The mipmap level. Default 0.
        format : str
            The format representation of the data. If not given or None,
            it is decuced from the given data. Can be RGB, RGBA, LUMINANCE,
            LUMINANCE_ALPHA, ALPHA. The OpenGL enum can also be given.
        clim : (min, max)
            Contrast limits for the data. If specified, min will end
            up being 0.0 (black) and max will end up as 1.0 (white).
            If not given or None, clim is determined automatically. For
            floats they become (0.0, 1.0). For integers the are mapped to
            the full range of the type.

        """

        # Check level, get texLevel instance
        assert isinstance(level, int) and level >= 0
        texLevel = self._levels.get(level, None)
        if texLevel is None:
            texLevel = self._levels[level] = TextureLevel(level)

        # Get ndim
        MAP = {gl.GL_TEXTURE_2D: 2, gl.ext.GL_TEXTURE_3D: 3}
        ndim = MAP.get(self._target, 0)

        # Check data
        shape = data.shape
        if not isinstance(data, np.ndarray):
            raise ValueError("Data should be a numpy array.")
        if not data.ndim in (ndim, ndim + 1):
            raise ValueError('Data shape must be ndim or ndim+1.')

        # Check format
        if format is None:
            format = get_formats(shape, self._target)[0]
        else:
            format = convert_to_enum(format)
            if format not in get_formats(shape, self._target):
                raise ValueError('Given format does not match with shape.')

        # Check clim
        assert clim is None or (isinstance(clim, tuple) and len(clim) == 2)

        # Get offset of all zeros
        offset = [0 for i in data.shape[:ndim]]

        # Set new shape and format, does not cause a resize if not necessary
        texLevel.set(shape, format)

        # Set pending data
        texLevel.pending_data.append((data, clim, offset))
        self._need_update = True

    def set_subdata(self, offset, data, level=0, format=None, clim=None):
        """ Set a region of data for this texture. This method can be
        called at any time (even if there is no context yet).

        In contrast to set_data(), each call to this method results in
        an OpenGL api call.

        Parameters
        ----------
        offset : tuple
            The offset for each dimension, to update part of the texture.
        data : numpy array
            The texture data to set. The data (with offset) cannot exceed
            the boundaries of the current texture.
        level : int
            The mipmap level. Default 0.
        format : OpenGL enum
            The format representation of the data. If not given or None,
            it is decuced from the given data. Can be RGB, RGBA, LUMINANCE,
            LUMINANCE_ALPHA, ALPHA. The OpenGL enum can also be given.
        clim : (min, max)
            Contrast limits for the data. If specified, min will end
            up being 0.0 (black) and max will end up as 1.0 (white).
            If not given or None, clim is determined automatically. For
            floats they become (0.0, 1.0). For integers the are mapped to
            the full range of the type.

        """

        # Check level, get texLevel instance
        assert isinstance(level, int) and level >= 0
        texLevel = self._levels.get(level, None)

        # Is there data?
        if not texLevel or not texLevel.shape:
            raise RuntimeError('Cannot set subdata if there is no '
                               'texture allocated yet.')

        # Get ndim
        MAP = {gl.GL_TEXTURE_2D: 2, gl.ext.GL_TEXTURE_3D: 3}
        ndim = MAP.get(self._target, 0)

        # Check data
        shape = data.shape
        if not isinstance(data, np.ndarray):
            raise ValueError("Data should be a numpy array.")
        if not data.ndim in (ndim, ndim + 1):
            raise ValueError('Data shape must be ndim or ndim+1.')

        # Check offset
        offset = tuple([int(i) for i in offset])
        if not len(offset) == ndim:
            raise ValueError('Offset must match with number of dimensions.')
        if not all([i >= 0 for i in offset]):
            raise ValueError('Offset cannot contain elements < 0.')
        fits = [(offset[i] + shape[i] <= texLevel.shape[i])
                for i in range(ndim)]
        if not all(fits):
            raise ValueError(
                "Given subdata does not fit in the existing texture.")

        # Get format if not given
        if format is None:
            if texLevel.format not in get_formats(shape, self._target):
                raise ValueError(
                    'Subdata shape does not match with current format.')
        else:
            format = convert_to_enum(format)
            if format != texLevel.format:
                raise ValueError(
                    'Subdata must have the same format as the existing data.')

        # Check clim
        assert clim is None or (isinstance(clim, tuple) and len(clim) == 2)

        # Set pending data
        texLevel.pending_data.append((data, clim, offset))
        self._need_update = True

    def _create(self):
        self._handle = gl.glGenTextures(1)

    def _delete(self):
        gl.glDeleteTextures([self._handle])

    def _activate(self):
        gl.glBindTexture(self._target, self._handle)

    def _deactivate(self):
        gl.glBindTexture(self._target, 0)

    def _update(self):

        # If we use a 3D texture, we need an extension
        if self._target == gl.ext.GL_TEXTURE_3D:
            if not ext_available('GL_texture_3D'):
                raise TextureError('3D Texture not available.')

        # For each level ...
        for texLevel in self._levels.values():

            # Need to resize?
            if texLevel.need_resize:
                texLevel.need_resize = False
                new_texture_created = False
                if self._valid and len(self._levels) == 1:
                    # We delete the existing texture first. In theory this
                    # should not be necessary, but some implementations cause
                    # memory leaks otherwise.
                    new_texture_created = True
                    self.delete()
                    self._create()
                # Allocate texture on GPU
                gl.glBindTexture(
                    self._target,
                    self._handle)  # self._activate()
                self._allocate_shape(texLevel)
                # If not ok, warn (one time)
                if not gl.glIsTexture(self._handle):
                    self._handle = 0
                    logger.warn('The texture is not valid.')
                    return
                if new_texture_created:
                    # We have a new texture: apply all parameters that were set
                    for param, value in self._texture_params.items():
                        gl.glTexParameter(self._target, param, value)
                        self._pending_params = {}  # We just applied all

            # Need to update some data?
            while texLevel.pending_data:
                data, clim, offset = texLevel.pending_data.pop(0)
                # Apply clim and convert data type to one supported by OpenGL
                data = convert_data(data, clim)
                # Upload
                gl.glBindTexture(
                    self._target,
                    self._handle)  # self._activate()
                self._upload_data(data, texLevel, offset)

        # Check
        # if not gl.glIsTexture(self._handle):
        #    raise TextureError('This should not happen (texture is invalid)')

        # Need to update any parameters?
        gl.glBindTexture(self._target, self._handle)  # self._activate()
        while self._pending_params:
            param, value = self._pending_params.popitem()
            gl.glTexParameter(self._target, param, value)

    def _allocate_shape(self, texLevel):
        """ Allocate space for the current texture object.
        It should have been verified that the texture will fit.
        """

        # Get parameters that we need
        target = self._target
        shape, format, level = texLevel.shape, texLevel.format, texLevel.level

        # Determine function and target from texType
        D = {  # gl.GL_TEXTURE_1D: (gl.glTexImage1D, 1),
            gl.GL_TEXTURE_2D: (gl.glTexImage2D, 2),
            gl.ext.GL_TEXTURE_3D: (gl.ext.glTexImage3D, 3)}
        uploadFun, ndim = D[target]

        # Determine type
        gltype = gl.GL_UNSIGNED_BYTE

        # Build args list
        size = [i for i in reversed(shape[:ndim])]
        args = [target, level, format] + size + [0, format, gltype, None]

        # Call
        uploadFun(*tuple(args))

    def _upload_data(self, data, texLevel, offset):
        """ Upload a texture to the current texture object.
        It should have been verified that the texture will fit.
        """

        # Get parameters that we need
        target = self._target
        format, level = texLevel.format, texLevel.level
        alignment = self._get_alignment(data.shape[-1])

        # Determine function and target from texType
        D = {  # gl.GL_TEXTURE_1D: (gl.glTexSubImage1D, 1),
            gl.GL_TEXTURE_2D: (gl.glTexSubImage2D, 2),
            gl.ext.GL_TEXTURE_3D: (gl.ext.glTexSubImage3D, 3)}
        uploadFun, ndim = D[target]

        # Reverse and check offset
        offset = offset[::-1]  # [i for i in offset]
        assert len(offset) == ndim

        # Determine type
        thetype = data.dtype.name
        # Note that we convert if necessary
        if thetype not in self.DTYPE2GTYPE:
            raise TextureError("Cannot translate datatype %s to GL." % thetype)
        gltype = self.DTYPE2GTYPE[thetype]

        # Build args list
        size = [i for i in reversed(data.shape[:ndim])]
        args = [target, level] + offset + size + [format, gltype, data]

        # Check the alignment of the texture
        if alignment != 4:
            gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, alignment)

        # Call
        uploadFun(*tuple(args))

        # Check if we need to reset our pixel store state
        if alignment != 4:
            gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 4)

    # from pylgy
    def _get_alignment(self, width):
        """Determines a textures byte alignment.

        If the width isn't a power of 2
        we need to adjust the byte alignment of the image.
        The image height is unimportant

        www.opengl.org/wiki/Common_Mistakes#Texture_upload_and_pixel_reads
        """

        # we know the alignment is appropriate
        # if we can divide the width by the
        # alignment cleanly
        # valid alignments are 1,2,4 and 8
        # put 4 first, since it's the default
        alignments = [4, 8, 2, 1]
        for alignment in alignments:
            if width % alignment == 0:
                return alignment


class Texture2D(Texture):

    """ Representation of a 2D texture. Inherits :class:`texture.Texture`.
    """

    def __init__(self, *args, **kwargs):
        Texture.__init__(self, gl.GL_TEXTURE_2D, *args, **kwargs)


class Texture3D(Texture):

    """ Representation of a 3D texture. Note that for this the
    GL_texture_3D extension needs to be available.
    Inherits :class:`texture.Texture`.
    """

    def __init__(self, *args, **kwargs):
        Texture.__init__(self, gl.ext.GL_TEXTURE_3D, *args, **kwargs)


class TextureCubeMap(Texture):

    """ Representation of a cube map, to store texture data for the
    6 sided of a cube. Used for instance to create environment mappings.
    Inherits :class:`texture.Texture`.

    This class is not yet implemented.
    """
    # Note that width and height for these textures should be equal

    def __init__(self, *args, **kwargs):
        raise NotImplementedError()
        Texture.__init__(self, gl.GL_TEXTURE_CUBE_MAP, *args, **kwargs)


# Utility functions
def get_formats(shape, target):
    """ Get formats for the texture, based on the target and the shape.
    If the shape does not match with the texture type, an exception is
    raised.
    """

    if target == gl.GL_TEXTURE_2D:
        if len(shape) == 2:
            return gl.GL_LUMINANCE, gl.GL_ALPHA
        elif len(shape) == 3 and shape[2] == 1:
            return gl.GL_LUMINANCE,
        elif len(shape) == 3 and shape[2] == 2:
            return gl.GL_LUMINANCE_ALPHA,
        elif len(shape) == 3 and shape[2] == 3:
            return gl.GL_RGB,
        elif len(shape) == 3 and shape[2] == 4:
            return gl.GL_RGBA,
        else:
            shapestr = 'x'.join([str(i) for i in shape])
            raise ValueError(
                "Cannot determine format for %s texture from shape %s." %
                ('2D', shapestr))

    elif target == gl.ext.GL_TEXTURE_3D:
        if len(shape) == 3:
            return gl.GL_LUMINANCE, gl.GL_ALPHA
        elif len(shape) == 4 and shape[3] == 1:
            return gl.GL_LUMINANCE,
        elif len(shape) == 4 and shape[3] == 2:
            return gl.GL_LUMINANCE_ALPHA,
        elif len(shape) == 4 and shape[3] == 3:
            return gl.GL_RGB,
        elif len(shape) == 4 and shape[3] == 4:
            return gl.GL_RGBA,
        else:
            shapestr = 'x'.join([str(i) for i in shape])
            raise ValueError(
                "Cannot determine format for %s texture from shape %s." %
                ('3D', shapestr))

    else:
        raise ValueError("Cannot determine format with these dimensions.")


def convert_data(data, clim=None):
    """ Convert data to a type that OpenGL can deal with.
    Also applies contrast limits if given.
    """

    # Prepare
    FLOAT32_SUPPORT = ext_available('texture_float')
    FLOAT16_SUPPORT = ext_available('texture_half_float')
    CONVERTING = False

    # Determine clim if not given, copy or make float32 if necessary.
    # Copies may be necessary because following operations are in-place.
    if data.dtype.name == 'bool':
        # Bools are ... unsigned ints
        data = data.astype(np.uint8)
        clim = None
    elif data.dtype.name == 'uint8':
        # Uint8 is what we need! If clim is None, no action required
        if clim is not None:
            data = data.astype(np.float32)
    elif data.dtype.name == 'float16':
        # Float16 may be allowed. If clim is None, no action is required
        if clim is not None:
            data = data.copy()
        elif not FLOAT16_SUPPORT:
            CONVERTING = True
            data = data.copy()
    elif data.dtype.name == 'float32':
        # Float32 may be allowed. If clim is None, no action is required
        if clim is not None:
            data = data.copy()
        elif not FLOAT32_SUPPORT:
            CONVERTING = True
            data = data.copy()
    elif 'float' in data.dtype.name:
        # All other floats are converted with relative ease
        CONVERTING = True
        data = data.astype(np.float32)
    elif 'int' in data.dtype.name:
        # Integers, we need to parse the dtype
        CONVERTING = True
        if clim is None:
            clim = (np.iinfo(data.dtype).min, np.iinfo(data.dtype).max)
        data = data.astype(np.float32)
    else:
        raise TextureError('Could not convert data type %s.' % data.dtype.name)

    # Apply limits if necessary
    if clim is not None:
        assert isinstance(clim, tuple)
        assert len(clim) == 2
        if clim[0] != 0.0:
            data -= clim[0]
        if clim[1] - clim[0] != 0.0:
            data *= 1.0 / (clim[1] - clim[0])

    if CONVERTING:
        logger.debug('Converting data.')

    # Convert if necessary
    if data.dtype == np.uint8:
        pass  # Always possible
    elif data.dtype == np.float16 and FLOAT16_SUPPORT:
        pass  # Yeah
    elif data.dtype == np.float32 and FLOAT32_SUPPORT:
        pass  # Yeah
    elif data.dtype in (np.float16, np.float32):
        # Arg, convert. Don't forget to clip
        data *= 255.0
        np.clip(data, 0, 255, data)
        data = data.astype(np.uint8)
    else:
        raise TextureError(
            'Error converting data type. This should not happen.')

    # Done
    return data
