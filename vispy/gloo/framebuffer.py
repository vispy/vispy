# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

#import OpenGL.GL as gl
from . import gl
from .globject import GLObject
from .texture import Texture2D
from ..util import logger

# ------------------------------------------------------ RenderBuffer class ---


class RenderBuffer(GLObject):
    """ Base class for render buffer object

    Parameters
    ----------
    format : GLEnum
        The buffer format: gl.GL_RGB565, gl.GL_RGBA4, gl.GL_RGB5_A1,
        gl.GL_DEPTH_COMPONENT16, or gl.GL_STENCIL_INDEX8
    shape : tuple of 2 ints
        Buffer shape (always two dimensional)
    resizeable : bool
        Indicates whether texture can be resized
    """

    def __init__(self, shape=None, format=None, resizeable=True):
        GLObject.__init__(self)
        self._shape = shape
        self._target = gl.GL_RENDERBUFFER
        self._format = format
        self._resizeable = resizeable
        self._need_resize = True

    @property
    def shape(self):
        """ Buffer shape """

        return self._shape

    def resize(self, shape):
        """ Resize the buffer (deferred operation)

        Parameters
        ----------

        shape : tuple of 2 integers
            New buffer shape (always two dimensional)
        """

        if not self._resizeable:
            raise RuntimeError("Buffer is not resizeable")

        if len(shape) != len(self.shape):
            raise ValueError("New shape has wrong number of dimensions")

        if shape == self.shape:
            return

        self._need_resize = True
        self._shape = shape

    def _create(self):
        """ Create buffer on GPU """

        logger.debug("GPU: Create render buffer")
        self._handle = gl.glCreateRenderbuffer()

    def _delete(self):
        """ Delete buffer from GPU """

        logger.debug("GPU: Deleting render buffer")
        gl.glDeleteRenderbuffer(self._handle)

    def _activate(self):
        """ Activate buffer on GPU """

        logger.debug("GPU: Activate render buffer")
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self._handle)
        
        # Resize if necessary
        if self._need_resize:
            self._resize()
            self._need_resize = False

    def _deactivate(self):
        """ Deactivate buffer on GPU """

        logger.debug("GPU: Deactivate render buffer")
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, 0)

    def _resize(self):
        """ Buffer resize on GPU """

        # WARNING: Shape should be checked against maximum size
        # maxsize = gl.glGetParameter(gl.GL_MAX_RENDERBUFFER_SIZE)
        logger.debug("GPU: Resize render buffer")
        gl.glRenderbufferStorage(self._target, self._format,
                                 self._shape[1], self._shape[0])


# ------------------------------------------------------- ColorBuffer class ---
class ColorBuffer(RenderBuffer):
    """ Color buffer object
    
    Parameters
    ----------

    format : GLEnum
        gl.GL_RGB565, gl.GL_RGBA4, gl.GL_RGB5_A1
    shape : tuple of 2 integers
        Buffer shape (always two dimensional)
    resizeable : bool
        Indicates whether buffer can be resized
    """

    def __init__(self, shape, format=gl.GL_RGBA, resizeable=True):
        # if format not in (gl.GL_RGB565, gl.GL_RGBA4, gl.GL_RGB5_A1):
        #     raise ValueError("Format not allowed for color buffer")
        RenderBuffer.__init__(self, shape, format, resizeable)


# ------------------------------------------------------- DepthBuffer class ---
class DepthBuffer(RenderBuffer):
    """ Depth buffer object
    
    Parameters
    ----------

    shape : tuple of 2 integers
        Buffer shape (always two dimensional)
    format : GLEnum
        gl.GL_DEPTH_COMPONENT16
    resizeable : bool
        Indicates whether buffer can be resized
    """

    def __init__(self, shape,
                 format=gl.GL_DEPTH_COMPONENT, resizeable=True):
        #if format not in (gl.GL_DEPTH_COMPONENT16,):
        #    raise ValueError("Format not allowed for depth buffer")
        RenderBuffer.__init__(self, shape, format, resizeable)


# ----------------------------------------------------- StencilBuffer class ---
class StencilBuffer(RenderBuffer):
    """ Stencil buffer object
    
    Parameters
    ----------

    shape : tuple of 2 integers
        Buffer shape (always two dimensional)
    format : GLEnum
        gl.GL_STENCIL_INDEX8
    resizeable : bool
        Indicates whether buffer can be resized
    """

    def __init__(self, shape,
                 format=gl.GL_STENCIL_INDEX8, resizeable=True):
        # if format not in (gl.GL_STENCIL_INDEX,):
        #     raise ValueError("Format not allowed for color buffer")
        RenderBuffer.__init__(self, shape, format, resizeable)


# ------------------------------------------------------- FrameBuffer class ---
class FrameBuffer(GLObject):
    """ Frame buffer object
    
    Parameters
    ----------
    
    color : ColorBuffer (optional)
        The color buffer to attach to this frame buffer
    depth : DepthBuffer (optional)
        The depth buffer to attach to this frame buffer
    stencil : StencilBuffer (optional)
        The stencil buffer to attach to this frame buffer
    resizable : bool
        Whether the buffers are resizable (default True)
    """

    def __init__(self, color=None, depth=None, stencil=None, resizeable=True):
        """
        """

        GLObject.__init__(self)

        self._shape = None
        self._color_buffer = color
        self._depth_buffer = depth
        self._stencil_buffer = stencil
        self._need_attach = True
        self._resizeable = resizeable
        self._pending_attachments = []

        if color is not None:
            self.color_buffer = color
        if depth is not None:
            self.depth_buffer = depth
        if stencil is not None:
            self.stencil_buffer = stencil

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
        """Color buffer attachment"""

        target = gl.GL_COLOR_ATTACHMENT0
        if isinstance(buffer, (ColorBuffer, Texture2D)) or buffer is None:
            self._color_buffer = buffer
            self._pending_attachments.append((target, buffer))
            self._need_attach = True
        else:
            raise TypeError("Buffer must be a ColorBuffer, Texture2D or None."
                            " (got %s)" % type(buffer))

    @property
    def depth_buffer(self):
        """Depth buffer attachment"""

        return self._depth_buffer

    @depth_buffer.setter
    def depth_buffer(self, buffer):
        """Depth buffer attachment"""

        target = gl.GL_DEPTH_ATTACHMENT
        if isinstance(buffer, (DepthBuffer, Texture2D)) or buffer is None:
            self._depth_buffer = buffer
            self._pending_attachments.append((target, buffer))
            self._need_attach = True
        else:
            raise TypeError("Buffer must be a DepthBuffer, Texture2D or None."
                            " (got %s)" % type(buffer))

    @property
    def stencil_buffer(self):
        """Stencil buffer attachment"""

        return self._stencil_buffer

    @stencil_buffer.setter
    def stencil_buffer(self, buffer):
        """Stencil buffer attachment"""

        target = gl.GL_STENCIL_ATTACHMENT
        if isinstance(buffer, StencilBuffer) or buffer is None:
            self._stencil_buffer = buffer
            self._pending_attachments.append((target, buffer))
            self._need_attach = True
        else:
            raise TypeError("Buffer must be a StencilBuffer, Texture2D or "
                            "None. (got %s)" % type(buffer))

    @property
    def shape(self):
        """ Buffer shape """

        return self._shape

    def resize(self, shape):
        """ Resize the buffer (deferred operation)

        Parameters
        ----------

        shape : tuple of 2 integers
            New buffer shape (always two dimensional)
        """

        if not self._resizeable:
            raise RuntimeError("FrameBuffer is not resizeable")

        if len(shape) != 2:
            raise ValueError("New shape has wrong number of dimensions")

        if self.color_buffer is not None:
            self.color_buffer.resize(shape)
        if self.depth_buffer is not None:
            self.depth_buffer.resize(shape)
        if self.stencil_buffer is not None:
            self.stencil_buffer.resize(shape)

    def _create(self):
        """ Create framebuffer on GPU """

        logger.debug("GPU: Create framebuffer")
        self._handle = gl.glCreateFramebuffer()

    def _delete(self):
        """ Delete buffer from GPU """

        logger.debug("GPU: Delete framebuffer")
        gl.glDeleteFramebuffer(self._handle)

    def _activate(self):
        """ Activate framebuffer on GPU """

        logger.debug("GPU: Activate render framebuffer")
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._handle)
        
        # Attach buffers if necessary
        if self._need_attach:
            self._attach()
            self._need_attach = False
    
    def _deactivate(self):
        """ Deactivate framebuffer on GPU """

        logger.debug("GPU: Deactivate render framebuffer")
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def _attach(self):
        """ Attach render buffers to framebuffer """
        
        # todo: this can currently only attach to texture mipmap level 0
        
        logger.debug("GPU: Attach render buffers")
        while self._pending_attachments:
            attachment, buffer = self._pending_attachments.pop(0)
            if buffer is None:
                gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, attachment,
                                             gl.GL_RENDERBUFFER, 0)
            elif isinstance(buffer, RenderBuffer):
                buffer.activate()
                gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, attachment,
                                             gl.GL_RENDERBUFFER, buffer.handle)
                buffer.deactivate()
            elif isinstance(buffer, Texture2D):
                buffer.activate()
                # INFO: 0 is for mipmap level 0 (default) of the texture
                gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, attachment,
                                          buffer.target, buffer.handle, 0)
                buffer.deactivate()
            else:
                raise ValueError("Invalid attachment: %s" % type(buffer))

        if 1:
            res = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
            if res == gl.GL_FRAMEBUFFER_COMPLETE:
                pass
            elif res == 0:
                raise RuntimeError('Target not equal to GL_FRAMEBUFFER')
            elif res == gl.GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT:
                raise RuntimeError(
                    'FrameBuffer attachments are incomplete.')
            elif res == gl.GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT:
                raise RuntimeError(
                    'No valid attachments in the FrameBuffer.')
            elif res == gl.GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS:
                raise RuntimeError(
                    'attachments do not have the same width and height.')
            #elif res == gl.GL_FRAMEBUFFER_INCOMPLETE_FORMATS: # not in es 2.0
            #    raise RuntimeError('Internal format of attachment '
            #                       'is not renderable.')
            elif res == gl.GL_FRAMEBUFFER_UNSUPPORTED:
                raise RuntimeError('Combination of internal formats used '
                                   'by attachments is not supported.')
            else:
                raise RuntimeError('Unknown framebuffer error: %r.' % res)
