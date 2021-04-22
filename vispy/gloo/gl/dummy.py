# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""A dummy backend."""

from . import BaseGLProxy, _copy_gl_functions
from ._constants import *  # noqa


class DummyProxy(BaseGLProxy):
    """A dummy backend that can be activated when the GL is not
    processed in this process. Each GL function call will raise an
    error.
    """

    def __call__(self, funcname, returns, *args):
        raise RuntimeError('Cannot call %r (or any other GL function), '
                           'since GL is disabled.' % funcname)


# Instantiate proxy and inject functions
_proxy = DummyProxy()
_copy_gl_functions(_proxy, globals())
