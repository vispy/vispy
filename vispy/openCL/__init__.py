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
    logger.error("Unable to import PyOpenCL. Please install it from: http://pypi.python.org/pypi/pyopencl")
    pyopencl = None

if not pyopencl.have_gl():
    logger.error("PyOpenCL is installed but was compiled with OpenGL support. Unusable !")
    pyopencl = None

def get_OCL_context():
    """
    Retrieves the OpenCL context
    """
    if not pyopencl:
        raise RuntimeError("OpenCL unuseable")
    ctx = None
    if sys.platform == "darwin":
        ctx = pyopencl.Context(properties=get_gl_sharing_context_properties(),
                         devices=[])
    else:
        # Some OSs prefer clCreateContextFromType, some prefer
        # clCreateContext. Try both and loop.
        for platform in pyopencl.get_platforms():
            try:
                ctx = pyopencl.Context(properties=[
                            (pyopencl.context_properties.PLATFORM, platform)]
                                       + get_gl_sharing_context_properties())
            except:
                for device in platform.get_devices():
                    try:
                        ctx = pyopencl.Context(properties=[
                            (pyopencl.context_properties.PLATFORM, platform)]
                                               + get_gl_sharing_context_properties(),
                            devices=[device])
                    except:
                        ctx = None
                    else:
                        break
            else:
                break
            if ctx:
                break
    return ctx

