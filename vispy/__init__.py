# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Vispy is a collaborative project that has the goal to allow more sharing
of code between visualization projects based on OpenGL. It does this
by providing powerful interfaces to OpenGL, at different levels of
abstraction and generality.

Vispy consists of the following modules:
  * vispy.gloo: Object oriented GL API
  * vispy.gloo.gl: Low level OpenGL API
  * vispy.app: for creating windows, timers and mainloops for various backends
  * vispy.util: various utilities
  * vispy.utils.dataio: read and write data
  * vispy.visuals: Higher level visualization objects (work in progress)
  * ... more to come

Vispy comes with a powerful event system and a simple application
framework that works on multiple backends. This allows easy creation
of figures, and enables integrating visualizations in a GUI application.

For more information see http://vispy.org.

"""

from __future__ import division

# Definition of the version number
__version__ = '0.2.1'


from .util import (dataio, parse_command_line_arguments, config,  # noqa
                   set_log_level, keys, sys_info)  # noqa

parse_command_line_arguments()
