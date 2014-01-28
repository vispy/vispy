# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
The app module defines three classes: Application, Canvas, and Timer.
On loading, vispy creates a default Application instance which can be used
via functions in the module's namespace.
"""

from __future__ import division

from .application import Application  # noqa
from .base import BaseApplicationBackend as ApplicationBackend  # noqa
from .base import BaseCanvasBackend as CanvasBackend  # noqa
from .base import BaseTimerBackend as TimerBackend  # noqa
from .canvas import Canvas, MouseEvent, KeyEvent  # noqa
from .timer import Timer  # noqa
from ._default_app import (default_app, use, create, run, quit,  # noqa
                           process_events)  # noqa
