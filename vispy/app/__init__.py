# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""The app module defines three classes: Application, Canvas, and Timer.
On loading, vispy creates a default Application instance which can be used
via functions in the module's namespace.
"""

from __future__ import division

from .application import Application  # noqa
from ._default_app import use_app, create, run, quit, process_events  # noqa
from .canvas import Canvas, MouseEvent, KeyEvent  # noqa
from .timer import Timer  # noqa
from . import base  # noqa
