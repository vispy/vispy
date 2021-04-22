# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""GL ES 2.0 API. 
On Windows implemented via Angle (i.e translated to DirectX).
"""

import sys
import os
import ctypes

from . import _copy_gl_functions
from ._constants import *  # noqa


# Ctypes stuff

if hasattr(ctypes, 'TEST_DLL'):
    # Load dummy lib 
    _lib = ctypes.TEST_DLL.LoadLibrary('')

elif sys.platform.startswith('win'):
    raise RuntimeError('ES 2.0 is not available on Windows yet')

    # todo: were are we going to put our libs?
    dirname = r'C:\Users\Almar\AppData\Local\Chromium\Application\34.0.1790.0'

    # Load dependency (so that libGLESv2 can find it
    fname = dirname + r'\d3dcompiler_46.dll'
    _libdum = ctypes.windll.LoadLibrary(fname)

    # Load GL ES 2.0 lib (Angle)
    fname = dirname + r'\libGLESv2.dll'
    _lib = ctypes.windll.LoadLibrary(fname)

elif sys.platform.startswith('linux'):
    es2_file = None
    # Load from env
    if 'ES2_LIBRARY' in os.environ:  # todo: is this the correct name?
        if os.path.exists(os.environ['ES2_LIBRARY']):
            es2_file = os.path.realpath(os.environ['ES2_LIBRARY'])
    # Else, try to find it
    if es2_file is None:
        es2_file = ctypes.util.find_library('GLESv2')
    # Else, we failed and exit
    if es2_file is None:
        raise OSError('GL ES 2.0 library not found')
    # Load it
    _lib = ctypes.CDLL(es2_file)

elif sys.platform.startswith('darwin'):
    raise RuntimeError('ES 2.0 is not available on OSX yet')

else:
    raise RuntimeError('Unknown platform: %s' % sys.platform)


# Inject

from . import _es2  # noqa
_copy_gl_functions(_es2, globals())
