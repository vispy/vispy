# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from functools import lru_cache

import numpy as np

from ..shaders import Function, FunctionChain, Varying
from .base_filter import Filter


class PlanesClipper(Filter):
    """Clips visual output based on arbitrary clipping planes."""

    VERT_CODE = """
    void clip() {
        // this is here to allow to set v_is_shown
        $v_is_shown;
        // Transform back to visual coordinates and clip based on that
        $clip_with_planes($itransform(gl_Position).xyz);
    }
    """

    FRAG_CODE = """
    void clip() {
        if ($v_is_shown < 0.)
            discard;
    }
    """

    def __init__(self, clipping_planes=None):
        super().__init__(
            vcode=Function(self.VERT_CODE), vhook='post', vpos=1,
            fcode=Function(self.FRAG_CODE), fhook='pre', fpos=1,
        )

        self.v_is_shown = Varying('v_is_shown', 'float')
        self.vshader['v_is_shown'] = self.v_is_shown
        self.fshader['v_is_shown'] = self.v_is_shown

        self.clipping_planes = clipping_planes

    @staticmethod
    def _get_itransform(visual):
        """
        get the transform from gl_Position to visual coordinates
        """
        return visual.get_transform('render', 'visual')

    def _attach(self, visual):
        super()._attach(visual)
        self.vshader['itransform'] = self._get_itransform(visual)

    @lru_cache(maxsize=10)
    def _build_clipping_planes_func(self, n_planes):
        """Build the function used to clip, based on the number of clipping planes.

        Each plane is defined by a position and a normal vector; the vertex is considered
        clipped if on the "negative" side of the plane
        """

        NOOP = """
        vec3 clip_noop(vec3 position) {
            return position;
        }
        """

        CLIP_CODE = """
        vec3 clip_with_plane(vec3 position) {
            vec3 relative_vec = position - $clipping_plane_pos;
            float is_shown = dot(relative_vec, $clipping_plane_norm);
            $v_is_shown = min(is_shown, $v_is_shown);
            // this return statement lets us construct a FunctionChain easily
            return position;
        }
        """

        clips = [Function(NOOP)]
        for _ in range(n_planes):
            clip = Function(CLIP_CODE)
            clip['v_is_shown'] = self.v_is_shown
            clips.append(clip)

        func = FunctionChain('clip_with_planes', clips)
        return func

    @property
    def clipping_planes(self):
        """Get the set of planes used to clip the mesh.
        Each plane is defined by a position and a normal vector (magnitude is irrelevant). Shape: (n_planes, 2, 3)
        """
        return self._clipping_planes[:, :, ::-1]

    @clipping_planes.setter
    def clipping_planes(self, value):
        if value is None:
            value = np.empty([0, 2, 3])
        value = value[:, :, ::-1]
        self._clipping_planes = value

        clipping_func = self._build_clipping_planes_func(len(value))

        for func, plane in zip(clipping_func[1:], value):  # skip noop func
            func['clipping_plane_pos'] = tuple(plane[0])
            func['clipping_plane_norm'] = tuple(plane[1])

        self.vshader['clip_with_planes'] = clipping_func
