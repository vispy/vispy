# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Definition of Frame Buffer Object class and RenderBuffer class.

"""

from __future__ import print_function, division, absolute_import

import sys
import numpy as np

from vispy import gl
from . import GLObject, push_enable, pop_enable, ext_available
from . import Texture2D

if sys.version_info > (3,):
    basestring = str


# todo: we need a way to keep track of who uses a RenderBuffer,
# so that it can be deleted when the last object stops using it.
# Same for Shader class.

class RenderBuffer(GLObject):
    """ Representation of a render buffer, to be attached to a
    FrameBuffer.
    """
    
    _COLOR_FORMATS = (gl.GL_RGB565, gl.GL_RGBA4, gl.GL_RGB5_A1,
                      gl.ext.GL_RGB8, gl.ext.GL_RGBA8)
    _DEPTH_FORMATS = (gl.GL_DEPTH_COMPONENT16, 
                      gl.ext.GL_DEPTH_COMPONENT24, gl.ext.GL_DEPTH_COMPONENT32)
    _STENCIL_FORMATS = (gl.GL_STENCIL_INDEX8, 
                        gl.ext.GL_STENCIL_INDEX1, gl.ext.GL_STENCIL_INDEX4)
    
    _FORMATS = (_COLOR_FORMATS + _DEPTH_FORMATS + _STENCIL_FORMATS +
                (gl.ext.GL_DEPTH24_STENCIL8,) )
    
    
    def __init__(self, internalformat=None, width=None, height=None):
        
        # ID (by which OpenGl identifies the texture)
        # 0 means uninitialized, <0 means error.
        self._handle = 0
        
        # Init data
        self._pending_data = None
        
        # Set storage now?
        info = internalformat, width, height
        if [i for i in info if i is not None]:
            if None in info:
                raise ValueError('Specify all or none arguments to RenderBuffer.')
            self.set_storage(*info)
    
    
    def _create(self):
        self._handle = gl.glGenRenderbuffers(1)
    
    
    def _delete(self):
       gl.glDeleteRenderbuffers([self._handle])
    
    # todo: User should in general not have to care about internalformat
    # source for errors!
    def set_storage(self, internalformat, width, height):
        # Check format
        if internalformat not in self._FORMATS:
            raise ValueError('Given format not supported for RenderBuffer storage.')
        # Check dimensions
        width, height = int(width), int(height)
        assert width > 0
        assert height > 0
        # Set pending data
        self._pending_data = internalformat, width, height
    
    
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
        if self._pending_data is not None:
            # Get data
            internalformat, width, height =  self._pending_data
            self._pending_data = None
            # Check size
            MAX = gl.glGetIntegerv(gl.GL_MAX_RENDERBUFFER_SIZE)
            if width > MAX or height > MAX:
                raise RuntimeError('Cannot create a render buffer of %ix%i (max is %i).' % (width, height, MAX))
            # Set 
            gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, internalformat, width, height)
    
    
    def _disable(self):
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, 0)



class FrameBuffer(GLObject):
    """ Representation of a frame buffer object (a.k.a. FBO).
    FrameBuffers allow off-screen rendering instead of to the screen.
    This is for instance used for special effects and post-processing.
    """
    
    def __init__(self):
        
        # ID (by which OpenGl identifies the object)
        # 0 means uninitialized, <0 means error.
        self._handle = 0
        
        # Init pending attachements
        self._pending_attachements = []
        self._attachement_color = None
        self._attachement_depth = None
        self._attachement_stencil = None
    
    
    def _create(self):
        self._handle = gl.glGenFramebuffers(1)
    
    
    def _delete(self):
       gl.glDeleteFramebuffers([self._handle])
    
    
    # todo: auto-create RenderBuffer?
    # todo: make API for Program and FrameBuffer more similar
    def attach_color(self, object, level=0):
        """ Attach a RenderBuffer of Texture instance to collect
        color output for this FrameBuffer. Pass None for object
        to detach the attachement. If a texture is given,
        level specifies the mipmap level (default 0).
        """
        attachment = gl.GL_COLOR_ATTACHMENT0
        assert isinstance(level, int)
        
        if object is None or object == 0:
            # Detach
            self._attachement_color = None
            self._pending_attachements.append( (attachment, 0, None) )
        elif isinstance(object, RenderBuffer):
            # Render buffer
            self._attachement_color = object
            self._pending_attachements.append( (attachment, object, None) )
        elif isinstance(object, Texture2D):
            # Texture
            self._attachement_color = object
            self._pending_attachements.append( (attachment, object, level) )
        else:
            raise ValueError('Can only attach a RenderBuffer of Texture to a FrameBuffer.')
    
    
    def attach_depth(self, object, level=0):
        """ Attach a RenderBuffer of Texture instance to collect
        depth output for this FrameBuffer. Pass None for object
        to detach the attachement. If a texture is given,
        level specifies the mipmap level (default 0).
        """
        attachment = gl.GL_DEPTH_ATTACHMENT
        assert isinstance(level, int)
        
        if object is None or object == 0:
            # Detach
            self._attachement_depth = None
            self._pending_attachements.append( (attachment, 0, None) )
        elif isinstance(object, RenderBuffer):
            # Render buffer
            self._attachement_depth = object
            self._pending_attachements.append( (attachment, object, None) )
        elif isinstance(object, Texture2D):
            # Texture
            self._attachement_depth = object
            self._attachement_depth = object
            self._pending_attachements.append( (attachment, object, level) )
        else:
            raise ValueError('Can only attach a RenderBuffer of Texture to a FrameBuffer.')
    
    
    def attach_stencil(self, object):
        """ Attach a RenderBuffer instance to collect stencil output for
        this FrameBuffer. Pass None for object to detach the
        attachement.
        """
        attachment = gl.GL_STENCIL_ATTACHMENT
        if object is None or object == 0:
            # Detach
            self._attachement_stencil = None
            self._pending_attachements.append( (attachment, 0, None) )
        elif isinstance(object, RenderBuffer):
            # Detach
            self._attachement_stencil = object
            self._pending_attachements.append( (attachment, object, None) )
        else:
            raise ValueError('For stencil data, can only attach a RenderBuffer to a FrameBuffer.')
    
    
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
        # todo: 3D texture (need extension)
        while self._pending_attachements:
            something_changed = True
            attachment, object, level = self._pending_attachements.pop(0)
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
                raise RuntimeError('Invalid attachement. This should not happen.')
        
        # Check
        if something_changed:
            res = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
            if res == gl.GL_FRAMEBUFFER_COMPLETE:
                pass
            elif res == 0:
                raise RuntimeError('Target not equal to GL_FRAMEBUFFER')
            elif res == gl.GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT:
                raise RuntimeError('FrameBuffer attachements are incomplete.')
            elif res == gl.GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT:
                raise RuntimeError('No valid attachements in the FrameBuffer.')
            elif res == gl.GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS:
                raise RuntimeError('Attachements do not have the same width and height.')   
            #elif res == gl.GL_FRAMEBUFFER_INCOMPLETE_FORMATS:  # Not in our namespace?
            #    raise RuntimeError('Internal format of attachement is not renderable.')
            elif res == gl.GL_FRAMEBUFFER_UNSUPPORTED:
                raise RuntimeError('Combination of internal formats used by attachements is not supported.')
    
    
    def _disable(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

