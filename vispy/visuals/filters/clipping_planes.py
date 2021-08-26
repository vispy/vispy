# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from functools import lru_cache

import numpy as np

from ..shaders import Function, Varying
from .base_filter import Filter


class PlanesClipper(Filter):
    """Clips visual output based on arbitrary clipping planes."""

    VERT_CODE = """
    void clip() {
        // Transform back to visual coordinates and clip based on that
        $v_is_shown = $clip_with_planes($itransform(gl_Position).xyz);
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

        v_is_shown = Varying('v_is_shown', 'float')
        self.vshader['v_is_shown'] = v_is_shown
        self.fshader['v_is_shown'] = v_is_shown

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

    @staticmethod
    @lru_cache(maxsize=10)
    def _build_clipping_planes_func(n_planes):
        """Build the code snippet used to clip the volume based on self.clipping_planes."""
        func_template = '''
            float clip_planes(vec3 loc) {{
                float is_shown = 1.0;
                {clips};
                return is_shown;
            }}
        '''
        # the vertex is considered clipped if on the "negative" side of the plane
        clip_template = '''
            vec3 relative_vec{idx} = loc - ( $clipping_plane_pos{idx} );
            float is_shown{idx} = dot(relative_vec{idx}, $clipping_plane_norm{idx});
            is_shown = min(is_shown{idx}, is_shown);
            '''
        all_clips = []
        for idx in range(n_planes):
            all_clips.append(clip_template.format(idx=idx))
        formatted_code = func_template.format(clips=''.join(all_clips))
        return Function(formatted_code)

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

        clip_func = self._build_clipping_planes_func(len(value))
        self.vshader['clip_with_planes'] = clip_func

        for idx, plane in enumerate(value):
            clip_func[f'clipping_plane_pos{idx}'] = tuple(plane[0])
            clip_func[f'clipping_plane_norm{idx}'] = tuple(plane[1])
