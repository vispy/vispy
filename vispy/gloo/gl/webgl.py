# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" GL ES 2.0 API implemented via WebGL.
"""

from . import BaseGLProxy, _copy_gl_functions
from ._constants import *  # noqa


class WebGLProxy(BaseGLProxy):
    """ Dummy proxy class for WebGL. More or less psuedo code for now :)
    But this should get whomever is going to work on WebGL a good place to
    start.
    Note that in order to use WebGL, we also need a WebGL app, probably
    also via some sort of proxy class. 
    """
    
    def __call__(self, funcname, returns, *args):
        
        self.websocket.send(funcname, *args)
        if returns:
            return self.websocket.wait_for_result()


# Instantiate proxy and inject functions
_proxy = WebGLProxy()
_copy_gl_functions(_proxy, globals())
