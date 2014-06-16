# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


"""
Simple visual based on GL_LINE_STRIP / GL_LINES


API issues to work out:

  * Currently this only uses GL_LINE_STRIP. Should add a 'method' argument like
    Image.method that can be used to select higher-quality triangle
    methods.

  * Add a few different position input components:
        - X values from vertex buffer of index values, Xmin, and Xstep
        - position from float texture

"""

from __future__ import division

from ... import gloo
from .visual import Visual


class Line(Visual):
    """
    Displays multiple line segments.
    """
    def __init__(self, pos=None, mode='line_strip', **kwds):
        super(Line, self).__init__()
        
        glopts = kwds.pop('gl_options', 'translucent')
        self.set_gl_options(glopts)
        if mode=='lines':
            self._primitive = gloo.gl.GL_LINES
        elif mode=='line_strip' or mode==None:
            self._primitive = gloo.gl.GL_LINE_STRIP
        else:
            print "Invalid mode - %s, Available modes - lines , line_strip" % (mode)
            raise

        if pos is not None or kwds:
            self.set_data(pos, **kwds)

    def set_data(self, pos=None, **kwds):
        kwds['index'] = kwds.pop('edges', kwds.get('index', None))
        kwds.pop('width', 1)  # todo: do something with width
        super(Line, self).set_data(pos, **kwds)
