# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division
from .modular_visual import ModularVisual


class Mesh(ModularVisual):
    """
    Displays a 3D triangle mesh.
    """
    def __init__(self, **kwds):
        super(Mesh, self).__init__()

        glopts = kwds.pop('gl_options', 'translucent')
        self.set_gl_options(glopts)

        if kwds:
            self.set_data(**kwds)

    def set_data(self, **kwds):
        kwds['index'] = kwds.pop('faces', kwds.get('index', None))
        super(Mesh, self).set_data(**kwds)
