
import ctypes

from . import _copy_gl_functions
from ._constants import *


## Ctypes stuff



# fname = r'C:\Qt\Qt5.2.1-64-noogl\5.2.1\msvc2012_64\bin\msvcr110.dll'
# _libgles2 = ctypes.windll.LoadLibrary(fname)
# fname = r'C:\Qt\Qt5.2.1-64-noogl\5.2.1\msvc2012_64\bin\msvcp110.dll'
# _libgles2 = ctypes.windll.LoadLibrary(fname)   
# fname = r'C:\Qt\Qt5.2.1-64-noogl\5.2.1\msvc2012_64\bin\d3dcompiler_46.dll'
# _libgles2 = ctypes.windll.LoadLibrary(fname) 
# 
# #fname = r'C:\almar\projects\py\vispy\gles2 and egl libs\Qt5.2.1 32bit gl es2 libs\libGLESv2.dll'
# fname = r'C:\Qt\Qt5.2.1-64-noogl\5.2.1\msvc2012_64\bin\libGLESv2.dll'
# _lib = ctypes.windll.LoadLibrary(fname)

fname = r'C:\Users\Almar\AppData\Local\Chromium\Application\34.0.1790.0\d3dcompiler_46.dll'
_libdum = ctypes.windll.LoadLibrary(fname) 

#fname = r'C:\almar\projects\py\vispy\gles2 and egl libs\Qt5.2.1 32bit gl es2 libs\libGLESv2.dll'
fname = r'C:\Users\Almar\AppData\Local\Chromium\Application\34.0.1790.0\libGLESv2.dll'
_lib = ctypes.windll.LoadLibrary(fname)

## Compatibility


def glShaderSource_compat(handle, code):
    """ Easy for real ES 2.0.
    """
    glShaderSource(handle, [code])
    return []


## Inject


from . import _angle
_copy_gl_functions(_angle, globals())
