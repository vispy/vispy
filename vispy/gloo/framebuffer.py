# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from .globject import GLObject
from .texture import Texture2D
from .wrappers import _check_valid, read_pixels
from ..ext.six import string_types

# ------------------------------------------------------ RenderBuffer class ---


class RenderBuffer(GLObject):
    """ Base class for render buffer object
    
    A render buffer can be in color, depth or stencil format. If this
    format is not specified, it is set when attached to the FrameBuffer.
    
    Parameters
    ----------
    shape : tuple
        The shape of the render buffer.
    format : {None, 'color', 'depth', 'stencil'}
        The format of the render buffer. See resize.
    resizeable : bool
        Indicates whether texture can be resized
    """
    
    _GLIR_TYPE = 'RenderBuffer'
    
    def __init__(self, shape=None, format=None, resizeable=True):
        GLObject.__init__(self)
        self._resizeable = bool(resizeable)
        self.resize(shape, format)
    
    @property
    def shape(self):
        """RenderBuffer shape """
        return self._shape
    
    @property
    def format(self):
        """ RenderBuffer format """

        return self._format

    def resize(self, shape, format=None):
        """ Set the render-buffer size and format

        Parameters
        ----------
        shape : tuple of integers
            New shape in yx order. A render buffer is always 2D. For
            symmetry with the texture class, a 3-element tuple can also
            be given, in which case the last dimension is ignored.
        format : {None, 'color', 'depth', 'stencil'}
            The buffer format. If None, the format will be set upon attaching
            it to a framebuffer.One can also specify the explicit enum:
            GL_RGB565, GL_RGBA4, GL_RGB5_A1, GL_DEPTH_COMPONENT16, or
            GL_STENCIL_INDEX8
        """
        
        if not self._resizeable:
            raise RuntimeError("Buffer is not resizeable")
        # Check shape
        if not (isinstance(shape, tuple) and len(shape) in (2, 3)):
            raise ValueError('RenderBuffer shape must be a 2/3 element tuple')
        # Check format
        if format is None:
            pass  # Set later
        elif isinstance(format, int):
            pass  # Do not check, maybe user needs desktop GL formats
        elif isinstance(format, string_types):
            formats = {'color', 'depth', 'stencil'}
            if format not in formats:
                raise ValueError('RenderBuffer format must be "color", "depth"'
                                 ' or "stencil", not %r' % format)
        
        # Store and send GLIR command
        self._shape = shape
        self._format = format
        if self._format is not None:
            self._context.glir.command('SIZE', self._id, 
                                       self._shape, self._format)


# ------------------------------------------------------- FrameBuffer class ---
class FrameBuffer(GLObject):
    """ Frame buffer object
    
    Parameters
    ----------
    
    color : RenderBuffer (optional)
        The color buffer to attach to this frame buffer
    depth : RenderBuffer (optional)
        The depth buffer to attach to this frame buffer
    stencil : RenderBuffer (optional)
        The stencil buffer to attach to this frame buffer
    resizable : bool
        Whether the buffers are resizable (default True)
    """
    
    _GLIR_TYPE = 'FrameBuffer'
    
    def __init__(self, color=None, depth=None, stencil=None, resizeable=True):
        GLObject.__init__(self)
        # Init buffers
        self._color_buffer = None
        self._depth_buffer = None
        self._stencil_buffer = None
        # Init args
        self._resizeable = bool(resizeable)
        if color is not None:
            self.color_buffer = color
        if depth is not None:
            self.depth_buffer = depth
        if stencil is not None:
            self.stencil_buffer = stencil
    
    def activate(self):
        """ Activate/use this frame buffer.
        """
        self._context.glir.command('FRAMEBUFFER', self._id, True)
    
    def deactivate(self):
        """ Stop using this frame buffer, the previous framebuffer will be
        made active.
        """
        self._context.glir.command('FRAMEBUFFER', self._id, False)
    
    def __enter__(self):
        self.activate()
        return self

    def __exit__(self, t, val, trace):
        self.deactivate()

    @property
    def color_buffer(self):
        """Color buffer attachment"""
        return self._color_buffer

    @color_buffer.setter
    def color_buffer(self, buffer):
        # Auto-format for render buffer
        if isinstance(buffer, RenderBuffer) and buffer._format is None:
            buffer.resize(buffer.shape, 'color')
        # Attach
        if isinstance(buffer, (Texture2D, RenderBuffer)) or buffer is None:
            self._color_buffer = buffer
            id = 0 if buffer is None else buffer.id
            self._context.glir.command('ATTACH', self._id, 'color', id)
        else:
            raise TypeError("Buffer must be a RenderBuffer, Texture2D or None."
                            " (got %s)" % type(buffer))

    @property
    def depth_buffer(self):
        """Depth buffer attachment"""
        return self._depth_buffer

    @depth_buffer.setter
    def depth_buffer(self, buffer):
        # Auto-format for render buffer
        if isinstance(buffer, RenderBuffer) and buffer._format is None:
            buffer.resize(buffer.shape, 'depth')
        # Attach
        if isinstance(buffer, (Texture2D, RenderBuffer)) or buffer is None:
            self._depth_buffer = buffer
            id = 0 if buffer is None else buffer.id
            self._context.glir.command('ATTACH', self._id, 'depth', id)
        else:
            raise TypeError("Buffer must be a RenderBuffer, Texture2D or None."
                            " (got %s)" % type(buffer))

    @property
    def stencil_buffer(self):
        """Stencil buffer attachment"""
        return self._stencil_buffer

    @stencil_buffer.setter
    def stencil_buffer(self, buffer):
        # Auto-format for render buffer
        if isinstance(buffer, RenderBuffer) and buffer._format is None:
            buffer.resize(buffer.shape, 'stencil')
        # Attach
        if isinstance(buffer, RenderBuffer) or buffer is None:
            self._stencil_buffer = buffer
            id = 0 if buffer is None else buffer.id
            self._context.glir.command('ATTACH', self._id, 'stencil', id)
        else:
            raise TypeError("Buffer must be a RenderBuffer, Texture2D or "
                            "None. (got %s)" % type(buffer))

    @property
    def shape(self):
        """ The shape of the Texture/RenderBuffer attached to this FrameBuffer
        """
        if self.color_buffer is not None:
            return self.color_buffer.shape
        if self.depth_buffer is not None:
            return self.depth_buffer.shape
        if self.stencil_buffer is not None:
            return self.stencil_buffer.shape
        raise RuntimeError('FrameBuffer without buffers has undefined shape')
    
    def resize(self, shape):
        """ Resize all attached buffers with the given shape

        Parameters
        ----------
        shape : tuple of integers
            New buffer shape, to be applied to all currently attached buffers.
        """
        
        # Check
        if not self._resizeable:
            raise RuntimeError("FrameBuffer is not resizeable")
        if not (isinstance(shape, tuple) and len(shape) in (2, 3)):
            raise ValueError('RenderBuffer shape must be a 2/3 element tuple')
        
        # Resize our buffers
        if self.color_buffer is not None:
            self.color_buffer.resize(shape)
        if self.depth_buffer is not None:
            self.depth_buffer.resize(shape)
        if self.stencil_buffer is not None:
            self.stencil_buffer.resize(shape)

    def read(self, mode='color', alpha=True):
        """ Return array of pixel values in an attached buffer
        
        Parameters
        ----------
        mode : str
            The buffer type to read. May be 'color', 'depth', or 'stencil'.
        alpha : bool
            If True, returns RGBA array. Otherwise, returns RGB.
        
        Returns
        -------
        buffer : array
            3D array of pixels in np.uint8 format. 
            The array shape is (h, w, 3) or (h, w, 4), with the top-left 
            corner of the framebuffer at index [0, 0] in the returned array.
        
        """
        _check_valid('mode', mode, ['color', 'depth', 'stencil'])
        buffer = getattr(self, mode+'_buffer')
        h, w = buffer._shape
        
        # todo: this is ostensibly required, but not available in gloo.gl
        #gl.glReadBuffer(buffer._target)
        
        return read_pixels((0, 0, w, h), alpha=alpha)
