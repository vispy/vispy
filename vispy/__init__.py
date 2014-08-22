# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""

=====
Vispy
=====

Vispy is a collaborative project that has the goal to allow more sharing
of code between visualization projects based on OpenGL. It does this
by providing powerful interfaces to OpenGL, at different levels of
abstraction and generality.

Vispy consists of the following modules:
  * vispy.app: for creating windows, timers and mainloops for various backends
  * vispy.gloo: Object oriented GL API
  * vispy.gloo.gl: Low level OpenGL API
  * vispy.util: various utilities
  * vispy.scene: Higher level visualization objects (work in progress)
  * vispy.mpl_plot: matplotlib interface (work in progress)
  * ... more to come

Vispy comes with a powerful event system and a simple application
framework that works on multiple backends. This allows easy creation
of figures, and enables integrating visualizations in a GUI application.

For more information see http://vispy.org.
"""

from __future__ import division

__all__ = ['use', 'sys_info', 'set_log_level', 'test']

# Definition of the version number
__version__ = '0.3'


from .util import (_parse_command_line_arguments, config,  # noqa
                   set_log_level, keys, sys_info, test)  # noqa
from .util._use import use  # noqa

_parse_command_line_arguments()
