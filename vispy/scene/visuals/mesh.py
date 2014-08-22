# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division
from .modular_visual import ModularVisual


class Mesh(ModularVisual):
    """
    Displays a 3D triangle mesh.
    """
    def __init__(self, gl_options='translucent', faces=None, index=None, 
                 pos=None, z=0.0, color=None, **kwargs):
        super(Mesh, self).__init__(**kwargs)
        self.set_gl_options(depth_test=True, cull_face='front_and_back')
        self.update_gl_options(gl_options)
        
        # todo: how should this be handled? Subclasses will often define
        # different set_data signatures.
        Mesh.set_data(self, faces=faces, index=index, pos=pos, z=z, color=color)

    def set_data(self, **kwds):
        kwds['index'] = kwds.pop('faces', kwds.get('index', None))
        super(Mesh, self).set_data(**kwds)
