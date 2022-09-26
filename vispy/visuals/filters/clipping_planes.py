# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import annotations

from typing import Optional

from functools import lru_cache

import numpy as np

from ..shaders import Function, Varying
from .base_filter import Filter


class PlanesClipper(Filter):
    """Clips visual output based on arbitrary clipping planes.

    Parameters
    ----------
    cliping_planes : ArrayLike
        Each plane is defined by a position and a normal vector (magnitude is irrelevant). Shape: (n_planes, 2, 3)
    coord_system : str
        Coordinate system used by the clipping planes (see visuals.transforms.transform_system.py)

    """

    VERT_CODE = """
    void clip() {
        // pass position as varying for interpolation
        $v_position = gl_Position;
    }
    """

    FRAG_CODE = """
    void clip() {
        float distance_from_clip = $clip_with_planes($itransform($v_position).xyz);
        if (distance_from_clip < 0.)
            discard;
    }
    """

    def __init__(self, clipping_planes: Optional[np.ndarray] = None, coord_system: str = 'scene'):
        tr = ['visual', 'scene', 'document', 'canvas', 'framebuffer', 'render']
        if coord_system not in tr:
            raise ValueError(f'Invalid coordinate system {coord_system}. Must be one of {tr}.')
        self._coord_system = coord_system

        super().__init__(
            vcode=Function(self.VERT_CODE), vhook='post', vpos=1,
            fcode=Function(self.FRAG_CODE), fhook='pre', fpos=1,
        )

        # initialize clipping planes
        self._clipping_planes = np.empty((0, 2, 3), dtype=np.float32)
        self._clipping_planes_func = Function(self._build_clipping_planes_glsl(0))
        self.fshader['clip_with_planes'] = self._clipping_planes_func

        v_position = Varying('v_position', 'vec4')
        self.vshader['v_position'] = v_position
        self.fshader['v_position'] = v_position

        self.clipping_planes = clipping_planes

    @property
    def coord_system(self) -> str:
        """
        Coordinate system used by the clipping planes (see visuals.transforms.transform_system.py)
        """
        # unsettable cause we can't update the transform after being attached
        return self._coord_system

    def _attach(self, visual):
        super()._attach(visual)
        self.fshader['itransform'] = visual.get_transform('render', self._coord_system)

    @staticmethod
    @lru_cache(maxsize=10)
    def _build_clipping_planes_glsl(n_planes: int) -> str:
        """Build the code snippet used to clip the volume based on self.clipping_planes."""
        func_template = '''
            float clip_planes(vec3 loc) {{
                float distance_from_clip = 3.4e38; // max float
                {clips};
                return distance_from_clip;
            }}
        '''
        # the vertex is considered clipped if on the "negative" side of the plane
        clip_template = '''
            vec3 relative_vec{idx} = loc - $clipping_plane_pos{idx};
            float distance_from_clip{idx} = dot(relative_vec{idx}, $clipping_plane_norm{idx});
            distance_from_clip = min(distance_from_clip{idx}, distance_from_clip);
            '''
        all_clips = []
        for idx in range(n_planes):
            all_clips.append(clip_template.format(idx=idx))
        formatted_code = func_template.format(clips=''.join(all_clips))
        return formatted_code

    @property
    def clipping_planes(self) -> np.ndarray:
        """Get the set of planes used to clip the mesh.
        Each plane is defined by a position and a normal vector (magnitude is irrelevant). Shape: (n_planes, 2, 3)
        """
        return self._clipping_planes

    @clipping_planes.setter
    def clipping_planes(self, value: Optional[np.ndarray]):
        if value is None:
            value = np.empty((0, 2, 3), dtype=np.float32)

        # only recreate function if amount of clipping planes changes
        if len(value) != len(self._clipping_planes):
            self._clipping_planes_func = Function(self._build_clipping_planes_glsl(len(value)))
            self.fshader['clip_with_planes'] = self._clipping_planes_func

        self._clipping_planes = value

        for idx, plane in enumerate(value):
            self._clipping_planes_func[f'clipping_plane_pos{idx}'] = tuple(plane[0])
            self._clipping_planes_func[f'clipping_plane_norm{idx}'] = tuple(plane[1])
