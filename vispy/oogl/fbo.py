# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Definition of Frame Buffer Object class and RenderBuffer class.

"""

from __future__ import print_function, division, absolute_import

import sys
import numpy as np

from vispy import gl
from . import GLObject, ext_available
from . import Texture2D

# todo: we need a way to keep track of who uses a RenderBuffer,
# so that it can be deleted when the last object stops using it.
# Same for Shader class.
# todo: support for 3D texture (need extension)
# todo: support Cubemap
        
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
                (gl.ext.GL_DEPTH24_STENCIL8,) )
    
    
    def __init__(self, shape=None, format=None):
        
        # ID (by which OpenGl identifies the texture)
        # 0 means uninitialized, <0 means error.
        self._handle = 0
        
        # Parameters
        self._shape = None
        self._format = None
        
        # Need update
        self._dirty = True
        
        # Set storage now?
        if shape is not None:
            self.set_storage(shape, format=format)
    
    
    def _create(self):
        self._handle = gl.glGenRenderbuffers(1)
    
    
    def _delete(self):
       gl.glDeleteRenderbuffers([self._handle])
    
    
    def set_storage(self, shape, format=None):
        """ Allocate storage for this render buffer.
        
        This function can be repeatedly called without much cost if
        the shape is not changed.
        
        In general, it's easier to just call FrameBuffer.set_size()
        to allocate space for all attachements.
        
        Parameters
        ----------
        shape : tuple
            The shape of the "virtual" data. Note that shape[0] is height.
        format : OpenGL enum
            The format representation of the data. If not given or None,
            it is determined automatically depending on the shape and
            the kind of atatchment. Can be GL_RGB565, GL_RGBA4,
            GL_RGB5_A1, GL_RGB8, GL_RGBA8, GL_DEPTH_COMPONENT16,
            GL_DEPTH_COMPONENT24, GL_DEPTH_COMPONENT32,
            GL_STENCIL_INDEX8, GL_STENCIL_INDEX1, GL_STENCIL_INDEX4.
        
        """
        # Set ndim
        ndim = 2
        
        # Is this already my shape?
        if format is None or format is self._format:
            if self._shape is not None:
                if self._shape[:ndim] == shape[:ndim]:
                    return
        
        # Check shape
        assert isinstance(shape, tuple)
        assert len(shape) in (ndim, ndim+1)
        shape = tuple([int(i) for i in shape])
        assert all([i>0 for i in shape])
        
        # Check format
        if format is None:
            pass  # Set later by FBO
        elif format not in self._FORMATS:
            raise ValueError('Given format not supported for RenderBuffer storage.')
        
        # Set pending data
        self._shape = shape
        self._format = format or self._format
        self._dirty = True
    
    
    def _enable(self):
        # Error last time?
        if self._handle < 0:
            return
        
        # Create?
        if self._handle == 0:
            self._create()
        
        # Enable
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self._handle)
        
        # Set storage?
        if self._dirty:
            # Get data
            shape, format =  self._shape, self._format
            if shape is None or format is None:
                return
            else:
                self._dirty = False # Only if we got here
            # Check size
            MAX = gl.glGetIntegerv(gl.GL_MAX_RENDERBUFFER_SIZE)
            if shape[0] > MAX or shape[1] > MAX:
                raise RuntimeError('Cannot create a render buffer of %ix%i (max is %i).' % (shape[1], shape[0], MAX))
            # Set 
            gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, format, shape[1], shape[0])
    
    
    def _disable(self):
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, 0)



class FrameBuffer(GLObject):
    """ Representation of a frame buffer object (a.k.a. FBO).
    FrameBuffers allow off-screen rendering instead of to the screen.
    This is for instance used for special effects and post-processing.
    """
    
    def __init__(self, color=None, depth=None, stencil=None):
        
        # ID (by which OpenGl identifies the object)
        # 0 means uninitialized, <0 means error.
        self._handle = 0
        
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
    
    def _create(self):
        self._handle = gl.glGenFramebuffers(1)
    
    
    def _delete(self):
       gl.glDeleteFramebuffers([self._handle])
    
    
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
        assert isinstance(level, int)
        
        if object is None or object == 0:
            # Detach
            self._attachment_color = None
            self._pending_attachments.append( (attachment, 0, None) )
        elif isinstance(object, RenderBuffer):
            # Render buffer
            self._attachment_color = object
            object._format = object._format or gl.GL_RGB565  # GL_RGB565 or GL_RGBA4
            self._pending_attachments.append( (attachment, object, None) )
        elif isinstance(object, Texture2D):
            # Texture
            self._attachment_color = object
            self._pending_attachments.append( (attachment, object, level) )
        else:
            raise ValueError('Can only attach a RenderBuffer of Texture to a FrameBuffer.')
    
    
    def attach_depth(self, object, level=0):
        """ Attach a RenderBuffer of Texture instance to collect
        depth output for this FrameBuffer. Pass None for object
        to detach the attachment. If a texture is given,
        level specifies the mipmap level (default 0).
        """
        attachment = gl.GL_DEPTH_ATTACHMENT
        assert isinstance(level, int)
        
        if object is None or object == 0:
            # Detach
            self._attachment_depth = None
            self._pending_attachments.append( (attachment, 0, None) )
        elif isinstance(object, RenderBuffer):
            # Render buffer
            object._format = object._format or gl.GL_DEPTH_COMPONENT16
            self._attachment_depth = object
            self._pending_attachments.append( (attachment, object, None) )
        elif isinstance(object, Texture2D):
            # Texture
            self._attachment_depth = object
            self._attachment_depth = object
            self._pending_attachments.append( (attachment, object, level) )
        else:
            raise ValueError('Can only attach a RenderBuffer or Texture to a FrameBuffer.')
    
    
    def attach_stencil(self, object):
        """ Attach a RenderBuffer instance to collect stencil output for
        this FrameBuffer. Pass None for object to detach the
        attachment.
        """
        attachment = gl.GL_STENCIL_ATTACHMENT
        if object is None or object == 0:
            # Detach
            self._attachment_stencil = None
            self._pending_attachments.append( (attachment, 0, None) )
        elif isinstance(object, RenderBuffer):
            object._format = object._format or gl.GL_STENCIL_INDEX8
            # Detach
            self._attachment_stencil = object
            self._pending_attachments.append( (attachment, object, None) )
        else:
            raise ValueError('For stencil data, can only attach a RenderBuffer to a FrameBuffer.')
    
    
    def set_size(self, width, height):
        """ Convenience function to set the space allocated for all
        attachments in use.
        """
        shape = height, width, 3
        for attachment in ( self._attachment_color, 
                            self._attachment_depth,
                            self._attachment_stencil):
            if isinstance(attachment, Texture2D):
                attachment.set_storage(shape)
            elif isinstance(attachment, RenderBuffer):
                attachment.set_storage(shape)
    
    
    def _enable(self):
        
        # Error last time?
        if self._handle < 0:
            return
        
        # Create?
        something_changed = False
        if self._handle == 0:
            self._create()
            something_changed = True
        
        # Enable
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._handle)
        
        # Attach any RenderBuffers or Textures
        # Note that we only enable the object briefly to attach it.
        # After that, the object does not need to be bound.
        while self._pending_attachments:
            something_changed = True
            attachment, object, level = self._pending_attachments.pop(0)
            if object == 0:
                gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, attachment,
                                            gl.GL_RENDERBUFFER, 0)
            elif isinstance(object, RenderBuffer):
                with object:
                    gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, attachment,
                                            gl.GL_RENDERBUFFER, object.handle)
            elif isinstance(object, Texture2D):
                # note that we use private variable _target from Texture
                with object:
                    gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, attachment,
                                    object._target, object.handle, level)
            else:
                raise RuntimeError('Invalid attachment. This should not happen.')
        
        # Check
        if something_changed:
            res = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
            if res == gl.GL_FRAMEBUFFER_COMPLETE:
                pass
            elif res == 0:
                raise RuntimeError('Target not equal to GL_FRAMEBUFFER')
            elif res == gl.GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT:
                raise RuntimeError('FrameBuffer attachments are incomplete.')
            elif res == gl.GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT:
                raise RuntimeError('No valid attachments in the FrameBuffer.')
            elif res == gl.GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS:
                raise RuntimeError('attachments do not have the same width and height.')   
            #elif res == gl.GL_FRAMEBUFFER_INCOMPLETE_FORMATS:  # Not in our namespace?
            #    raise RuntimeError('Internal format of attachment is not renderable.')
            elif res == gl.GL_FRAMEBUFFER_UNSUPPORTED:
                raise RuntimeError('Combination of internal formats used by attachments is not supported.')
    
    
    def _disable(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

