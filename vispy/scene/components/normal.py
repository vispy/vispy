# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Normal components are modular shader components used for retrieving or
generating surface normal vectors.

These components generate a function in the fragment shader that accepts no
arguments and returns a vec4 normal vector. Typically, the normal vector
is computed in the vertex shader and passed by varying to the fragment
shader.
"""

from __future__ import division

from .component import VisualComponent
from ..shaders import Varying
from ... import gloo


class VertexNormalComponent(VisualComponent):
    SHADERS = dict(
        frag_normal="""
            vec4 normal() {
                return $norm;
            }
        """,
        vert_post_hook="""
            void normal_support() {
                //vec3 o = vec3(0,0,0);
                //vec3 i = o + $input_normal.xyz;
                //$output_normal = $map_local_to_nd(vec4(i,1)) -
                //                 $map_local_to_nd(vec4(o,1));
                $output_normal = vec4($input_normal, 1);
            }
        """)

    # exclude frag_normal when auto-attaching shaders because the visual
    # does not have a 'frag_normal' hook; instead this function will be called
    # by another component.
    AUTO_ATTACH = ['vert_post_hook']

    def __init__(self, meshdata, smooth=True):
        super(VertexNormalComponent, self).__init__()
        self._meshdata = meshdata
        self.smooth = smooth
        self._vbo = None
        self._vbo_mode = None

        # Create Varying to connect vertex / fragment shaders
        var = Varying('norm', dtype='vec4')
        self._funcs['frag_normal']['norm'] = var
        self._funcs['vert_post_hook']['output_normal'] = var

    def _make_vbo(self, mode):
        if self._vbo is None or self._vbo_mode != mode:
            if mode is self.DRAW_PRE_INDEXED:
                index = 'faces'
            else:
                index = None
            if self.smooth:
                norm = self._meshdata.vertex_normals(indexed=index)
            else:
                if index != 'faces':
                    raise Exception("Not possible to draw faceted mesh without"
                                    "pre-indexing.")
                norm = self._meshdata.face_normals(indexed=index)
            self._vbo = gloo.VertexBuffer(norm)
            self._vbo_mode = mode
        return self._vbo

    def normal_shader(self):
        """
        Return the fragment shader function that returns a normal vector.
        """
        return self._funcs['frag_normal']

    def activate(self, program, mode):
        vf = self._funcs['vert_post_hook']
        vf['input_normal'] = self._make_vbo(mode)  # attribute vec4
        vf['map_local_to_nd'] = self.visual._program.vert['map_local_to_nd']

    @property
    def supported_draw_modes(self):
        if self.smooth:
            return set([self.DRAW_PRE_INDEXED, self.DRAW_UNINDEXED])
        else:
            # not possible to draw faceted mesh without pre-indexing.
            return set([self.DRAW_PRE_INDEXED])
