# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Helper for the vispy.gl._gl module.
"""

import sys
import vispy
from OpenGL import GL as _GL



def _make_unavailable_func(funcname):
    def cb(*args, **kwds):
       raise RuntimeError('OpenGL API call "%s" is not available.' % funcname)
    return cb


def get_gl_functions_from_pyopengl(NS, funcnames):
    """ Get GL functions from pyopengl.
    """
    show_warnings = vispy.config['show_warnings']
    import OpenGL.GL.framebufferobjects as FBO
    
    for funcname in funcnames:
        func = None
        # Get function from GL
        try:
            func = getattr(_GL, funcname)
        except AttributeError:
            # Get function from FBO
            try:
                func = getattr(FBO, funcname)
            except AttributeError:
                # Some functions are known by a slightly different name
                # e.g. glDepthRangef, glDepthRangef
                if funcname.endswith('f'):
                    try:
                        func = getattr(_GL, funcname[:-1])
                    except AttributeError:
                        pass
        
        # Set dummy function if we could not find it
        if func is None:
            func = _make_unavailable_func(funcname)
            if True or show_warnings:  
                print('warning: %s not available' % funcname )
        # Set
        NS[funcname] = func


def fix(NS):
    """ Apply some fixes and patches.
    """
    
    # Fix glGetActiveAttrib, since if its just the ctypes function
    if (    ('glGetActiveAttrib' in NS) and 
            hasattr(NS['glGetActiveAttrib'], 'restype') ):
        import ctypes
        def new_glGetActiveAttrib(program, index):
            # Prepare
            bufsize = 32
            length = ctypes.c_int()
            size = ctypes.c_int()
            type = ctypes.c_int()
            name = ctypes.create_string_buffer(bufsize)
            # Call
            _GL.glGetActiveAttrib(program, index, 
                    bufsize, ctypes.byref(length), ctypes.byref(size), 
                    ctypes.byref(type), name)
            # Return Python objects
            #return name.value.decode('utf-8'), size.value, type.value
            return name.value, size.value, type.value
        
        # Patch
        NS['glGetActiveAttrib'] = new_glGetActiveAttrib
    
    
    # Monkey-patch pyopengl to fix a bug in glBufferSubData
    if sys.version_info > (3,):
        _m = sys.modules[NS['glBufferSubData'].wrapperFunction.__module__]
        _m.long = int
