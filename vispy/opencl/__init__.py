# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# Author: Jérôme Kieffer
# -----------------------------------------------------------------------------
""" Definition of OpenCL interaction using pyopencl """

from __future__ import division, print_function
import sys
from ..util import logger

try:
    import pyopencl, pyopencl.array
    from pyopencl.tools import get_gl_sharing_context_properties
except ImportError:
    logger.warning("Unable to import PyOpenCL. Please install it from: http://pypi.python.org/pypi/pyopencl")
    pyopencl = None

if not pyopencl.have_gl():
    logger.warning("PyOpenCL is installed but was compiled with OpenGL support. Unusable !")
    pyopencl = None

context = None

def get_context(platform=None, device=None):
    """
    Retrieves the OpenCL context
    
    Parameters
    ----------
    platform : platform number
        int
    device : device number in the platform
        int
    """
    if not pyopencl:
        raise RuntimeError("OpenCL unuseable")
    ctx = None
    properties = get_gl_sharing_context_properties()
    if (platform is not None) and (device is not None):
        platform = pyopencl.get_platforms()[platform]
        device = platform.get_devices()[device]
        try:
            ctx = pyopencl.Context(devices=[device],
                   properties=[(pyopencl.context_properties.PLATFORM, platform)]
                                    + properties)
        except:
            ctx = None
    elif sys.platform == "darwin":
        ctx = pyopencl.Context(properties=properties,
                         devices=[])
    else:
        # Some OSs prefer clCreateContextFromType, some prefer
        # clCreateContext. Try both and loop.
        for platform in pyopencl.get_platforms():
            try:
                ctx = pyopencl.Context(properties=properties +
                           [(pyopencl.context_properties.PLATFORM, platform)])
            except:
                for device in platform.get_devices():
                    try:
                        ctx = pyopencl.Context(devices=[device],
                                               properties=properties +
                            [(pyopencl.context_properties.PLATFORM, platform)])
                    except:
                        ctx = None
                    else:
                        break
            else:
                break
            if ctx:
                break
    if ctx:
        globals()["context"] = ctx
    return ctx

