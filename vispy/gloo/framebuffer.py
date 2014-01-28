# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Definition of Frame Buffer Object class and RenderBuffer class.

"""

from __future__ import division


from . import gl
from . import GLObject, convert_to_enum
from . import Texture2D

# todo: check and test all _delete methods

# todo: we need a way to keep track of who uses a RenderBuffer,
# so that it can be deleted when the last object stops using it.
# Same for Shader class.
# todo: support for 3D texture (need extension)
# todo: support Cubemap


class FrameBufferError(RuntimeError):

    """ Raised when something goes wrong that depens on state that was set
    earlier (due to deferred loading).
    """
    pass


class RenderBuffer(GLObject):

    """ Representation of a render buffer, to be attached to a
    FrameBuffer object.
    """

    _COLOR_FORMATS = (gl.GL_RGB565, gl.GL_RGBA4, gl.GL_RGB5_A1,
                      gl.ext.GL_RGB8, gl.ext.GL_RGBA8)
    _DEPTH_FORMATS = (gl.GL_DEPTH_COMPONENT16,
                      gl.ext.GL_DEPTH_COMPONENT24, gl.ext.GL_DEPTH_COMPONENT32)
    _STENCIL_FORMATS = (gl.GL_STENCIL_INDEX8,
                        gl.ext.GL_STENCIL_INDEX1, gl.ext.GL_STENCIL_INDEX4)

    _FORMATS = (_COLOR_FORMATS + _DEPTH_FORMATS + _STENCIL_FORMATS +
                (gl.ext.GL_DEPTH24_STENCIL8,))

    def __init__(self, shape=None, format=None):
        GLObject.__init__(self)

        # Parameters
        self._shape = None
        self._format = None

        # Set storage now?
        if shape is not None:
            self.set_shape(shape, format=format)

    def set_shape(self, shape, format=None):
        """ Allocate storage for this render buffer.

        This function can be repeatedly called without much cost if
        the shape is not changed.

        In general, it's easier to just call FrameBuffer.set_size()
        to allocate space for all attachements.

        Parameters
        ----------
        shape : tuple
            The shape of the "virtual" data. Note that shape[0] is height.
        format : str
            The format representation of the data. If not given or None,
            it is determined automatically depending on the shape and
            the kind of atatchment. Can be RGB565, RGBA4, RGB5_A1, RGB8,
            RGBA8, DEPTH_COMPONENT16, DEPTH_COMPONENT24, DEPTH_COMPONENT32,
            STENCIL_INDEX8, STENCIL_INDEX1, STENCIL_INDEX4. The OpenGL enum
            can also be given.

        """
        # Set ndim
        ndim = 2

        # Convert format
        format = convert_to_enum(format, True)

        # Check shape
        if not isinstance(shape, tuple):
            raise ValueError("Shape must be a tuple.")
        if not ((len(shape) == ndim) or
                len(shape) == ndim + 1 and shape[-1] <= 4):
            raise ValueError("Shape has invalid dimensions.")
        shape = tuple([int(i) for i in shape])
        if not all([i > 0 for i in shape]):
            raise ValueError("Cannot have negative shape.")

        # Is this already my shape?
        if format is None or format is self._format:
            if self._shape is not None:
                if self._shape[:ndim] == shape[:ndim]:
                    return

        # Check format
        if format is None:
            # Set later by FBO.
            # Note here, because default differs per color/depth/stencil
            pass
        elif format not in self._FORMATS:
            raise ValueError(
                'Given format not supported for RenderBuffer storage.')

        # Set pending data
        self._shape = shape
        self._format = format or self._format
        self._need_update = True

    def _create(self):
        self._handle = gl.glGenRenderbuffers(1)

    def _delete(self):
        gl.glDeleteRenderbuffers([self._handle])

    def _activate(self):
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self._handle)

    def _deactivate(self):
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, 0)

    def _update(self):

        # Enable now
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self._handle)

        # Get data
        shape, format = self._shape, self._format
        if shape is None or format is None:
            return
        # Check size
        MAX = gl.glGetIntegerv(gl.GL_MAX_RENDERBUFFER_SIZE)
        if shape[0] > MAX or shape[1] > MAX:
            raise FrameBufferError(
                'Cannot create a render buffer of %ix%i (max is %i).' %
                (shape[1], shape[0], MAX))
        # Set
        gl.glRenderbufferStorage(
            gl.GL_RENDERBUFFER,
            format,
            shape[1],
            shape[0])


class FrameBuffer(GLObject):

    """ Representation of a frame buffer object (a.k.a. FBO).
    FrameBuffers allow off-screen rendering instead of to the screen.
    This is for instance used for special effects and post-processing.
    """

    def __init__(self, color=None, depth=None, stencil=None):
        GLObject.__init__(self)

        # Init pending attachments
        self._pending_attachments = []
        self._attachment_color = None
        self._attachment_depth = None
        self._attachment_stencil = None

        # Set given attachments
        if color is not None:
            self.attach_color(color)
        elif depth is not None:
            self.attach_depth(depth)
        elif stencil is not None:
            self.attach_stencil(stencil)

    @property
    def color_attachment(self):
        """ Get the color attachement.
        """
        return self._attachment_color

    @property
    def depth_attachment(self):
        """ Get the depth attachement.
        """
        return self._attachment_depth

    @property
    def stencil_attachment(self):
        """ Get the stencil attachement.
        """
        return self._attachment_stencil

    def attach_color(self, object, level=0):
        """ Attach a RenderBuffer of Texture instance to collect
        color output for this FrameBuffer. Pass None for object
        to detach the attachment. If a texture is given,
        level specifies the mipmap level (default 0).
        """
        attachment = gl.GL_COLOR_ATTACHMENT0
        if not isinstance(level, int):
            raise ValueError("Level must be an int")

        if object is None or object == 0:
            # Detach
            self._attachment_color = None
            self._pending_attachments.append((attachment, 0, None))
        elif isinstance(object, RenderBuffer):
            # Render buffer
            self._attachment_color = object
            # GL_RGB565 or GL_RGBA4
            object._format = object._format or gl.GL_RGB565
            self._pending_attachments.append((attachment, object, None))
        elif isinstance(object, Texture2D):
            # Texture
            self._attachment_color = object
            self._pending_attachments.append((attachment, object, level))
        else:
            raise ValueError(
                'Can only attach a RenderBuffer of Texture to a FrameBuffer.')
        self._need_update = True

    def attach_depth(self, object, level=0):
        """ Attach a RenderBuffer of Texture instance to collect
        depth output for this FrameBuffer. Pass None for object
        to detach the attachment. If a texture is given,
        level specifies the mipmap level (default 0).
        """
        attachment = gl.GL_DEPTH_ATTACHMENT
        if not isinstance(level, int):
            raise ValueError("Level must be an int")

        if object is None or object == 0:
            # Detach
            self._attachment_depth = None
            self._pending_attachments.append((attachment, 0, None))
        elif isinstance(object, RenderBuffer):
            # Render buffer
            object._format = object._format or gl.GL_DEPTH_COMPONENT16
            self._attachment_depth = object
            self._pending_attachments.append((attachment, object, None))
        elif isinstance(object, Texture2D):
            # Texture
            self._attachment_depth = object
            self._attachment_depth = object
            self._pending_attachments.append((attachment, object, level))
        else:
            raise ValueError(
                'Can only attach a RenderBuffer or Texture to a FrameBuffer.')
        self._need_update = True

    def attach_stencil(self, object):
        """ Attach a RenderBuffer instance to collect stencil output for
        this FrameBuffer. Pass None for object to detach the
        attachment.
        """
        attachment = gl.GL_STENCIL_ATTACHMENT
        if object is None or object == 0:
            # Detach
            self._attachment_stencil = None
            self._pending_attachments.append((attachment, 0, None))
        elif isinstance(object, RenderBuffer):
            object._format = object._format or gl.GL_STENCIL_INDEX8
            # Detach
            self._attachment_stencil = object
            self._pending_attachments.append((attachment, object, None))
        else:
            raise ValueError('For stencil data, can only attach a '
                             'RenderBuffer to a FrameBuffer.')
        self._need_update = True

    def set_size(self, width, height):
        """ Convenience function to set the space allocated for all
        attachments in use.
        """
        shape = height, width, 3
        for attachment in (self._attachment_color,
                           self._attachment_depth,
                           self._attachment_stencil):
            if isinstance(attachment, Texture2D):
                attachment.set_shape(shape)
            elif isinstance(attachment, RenderBuffer):
                attachment.set_shape(shape)

    def _create(self):
        self._handle = gl.glGenFramebuffers(1)

    def _delete(self):
        gl.glDeleteFramebuffers([self._handle])

    def _activate(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._handle)

    def _deactivate(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def _update(self):

        # We need to activate before we can add attachements
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._handle)

        # Attach any RenderBuffers or Textures
        # Note that we only enable the object briefly to attach it.
        # After that, the object does not need to be bound.
        while self._pending_attachments:
            attachment, object, level = self._pending_attachments.pop(0)
            if object == 0:
                gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, attachment,
                                             gl.GL_RENDERBUFFER, 0)
            elif isinstance(object, RenderBuffer):
                with object:
                    gl.glFramebufferRenderbuffer(
                        gl.GL_FRAMEBUFFER,
                        attachment,
                        gl.GL_RENDERBUFFER,
                        object.handle)
            elif isinstance(object, Texture2D):
                # note that we use private variable _target from Texture
                with object:
                    gl.glFramebufferTexture2D(
                        gl.GL_FRAMEBUFFER,
                        attachment,
                        object._target,
                        object.handle,
                        level)
            else:
                raise FrameBufferError(
                    'Invalid attachment. This should not happen.')

        # Check
        if True:
            res = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
            if res == gl.GL_FRAMEBUFFER_COMPLETE:
                pass
            elif res == 0:
                raise FrameBufferError('Target not equal to GL_FRAMEBUFFER')
            elif res == gl.GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT:
                raise FrameBufferError(
                    'FrameBuffer attachments are incomplete.')
            elif res == gl.GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT:
                raise FrameBufferError(
                    'No valid attachments in the FrameBuffer.')
            elif res == gl.GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS:
                raise FrameBufferError(
                    'attachments do not have the same width and height.')
            # Not in our namespace?
            # elif res == gl.GL_FRAMEBUFFER_INCOMPLETE_FORMATS:
            #    raise FrameBufferError('Internal format of attachment '
            #                           'is not renderable.')
            elif res == gl.GL_FRAMEBUFFER_UNSUPPORTED:
                raise FrameBufferError('Combination of internal formats used '
                                       'by attachments is not supported.')
