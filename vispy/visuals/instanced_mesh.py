# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

"""An instanced version of MeshVisual with arbitrary shifts, transforms, and colors."""

from __future__ import division

import numpy as np

from ..gloo import VertexBuffer
from ..gloo.texture import downcast_to_32bit_if_needed
from ..color import ColorArray
from .filters import InstancedShadingFilter

from .mesh import MeshVisual


_VERTEX_SHADER = """
uniform bool use_instance_colors;

// these attributes will be defined on an instance basis
attribute vec3 shift;
attribute vec4 instance_color;
attribute vec3 transform_x;
attribute vec3 transform_y;
attribute vec3 transform_z;

vec4 color;

varying vec4 v_base_color;
void main() {
    if (use_instance_colors) {
        color = instance_color;
    } else {
        color = $base_color;
    }

    v_base_color = $color_transform(color);

    // transform is generated from column vectors (new basis vectors)
    // https://en.wikibooks.org/wiki/GLSL_Programming/Vector_and_Matrix_Operations#Constructors
    mat3 instance_transform = mat3(transform_x, transform_y, transform_z);
    vec3 pos_rotated = instance_transform * $to_vec4($position).xyz;
    vec4 pos_shifted = $to_vec4(pos_rotated + shift);
    gl_Position = $transform(pos_shifted);
}
"""


class InstancedMeshVisual(MeshVisual):
    """Instanced Mesh visual.

    Mostly identical to MeshVisual, but additionally takes arrays of
    of positions and transforms (optionally colors) to create multiple
    instances of the mesh.

    Instancing is a rendering technique that re-uses the same mesh data
    by applying transformations to vertices and vertex data or textures,
    wich can drastically improve performance compared to having many
    simple MeshVisuals.

    Parameters
    ----------
    instance_positions : (I, 3) array
        Coordinates for each instance of the mesh.
    instance_transforms : (I, 3, 3) array
        Matrices for the transforms to apply to each instance.
    instance_colors : ColorArray
        Matrices of colors for each instance. Colors
    *args : list
        Positional arguments to pass to `MeshVisual`.
    **kwargs : dict
        Keyword arguments to pass to `MeshVisual`.

    Examples
    --------
    See example `scene/instanced_mesh_visual.py` in the gallery.
    """

    _shaders = {
        'vertex': _VERTEX_SHADER,
        'fragment': MeshVisual._shaders['fragment'],
    }

    _shading_filter_class = InstancedShadingFilter

    def __init__(self, *args, instance_positions=None, instance_transforms=None, instance_colors=None, **kwargs):
        self._instance_positions = None
        self._instance_positions_vbo = None
        self._instance_transforms = None
        self._instance_transforms_vbos = None
        self._instance_colors = None
        self._instance_colors_vbo = None
        super().__init__(*args, **kwargs)
        self.instance_positions = instance_positions
        self.instance_transforms = instance_transforms
        self.instance_colors = instance_colors

    @property
    def instance_positions(self):
        return self._instance_positions

    @instance_positions.setter
    def instance_positions(self, pos):
        pos = np.atleast_2d(pos)
        if pos.ndim != 2 or pos.shape[-1] != 3:
            raise ValueError(f'positions must be 3D coordinates, but provided data has shape {pos.shape}')
        self._instance_positions = downcast_to_32bit_if_needed(pos)
        self._instance_positions_vbo = VertexBuffer(self._instance_positions, divisor=1)
        self.mesh_data_changed()

    @property
    def instance_transforms(self):
        return self._instance_transforms

    @instance_transforms.setter
    def instance_transforms(self, matrix):
        matrix = np.atleast_3d(matrix)
        if matrix.ndim != 3 or matrix.shape[1:] != (3, 3):
            raise ValueError(f'transforms must be an array of 3x3 matrices, but provided data has shape {matrix.shape}')
        self._instance_transforms = downcast_to_32bit_if_needed(matrix)
        # copy if not c contiguous
        self._instance_transforms_vbos = (
            VertexBuffer(np.ascontiguousarray(self._instance_transforms[..., 0]), divisor=1),
            VertexBuffer(np.ascontiguousarray(self._instance_transforms[..., 1]), divisor=1),
            VertexBuffer(np.ascontiguousarray(self._instance_transforms[..., 2]), divisor=1),
        )
        self.mesh_data_changed()

    @property
    def instance_colors(self):
        return self._instance_colors

    @instance_colors.setter
    def instance_colors(self, colors):
        if colors is not None:
            colors = ColorArray(colors)
            self._instance_colors_vbo = VertexBuffer(colors.rgba, divisor=1)

        self._instance_colors = colors
        self.mesh_data_changed()

    def _update_data(self):
        with self.events.data_updated.blocker():
            super()._update_data()

        # set instance buffers
        if self._instance_colors is not None:
            self.shared_program['use_instance_colors'] = True
            self.shared_program['instance_color'] = self._instance_colors_vbo
        else:
            self.shared_program['use_instance_colors'] = False

        self.shared_program['transform_x'] = self._instance_transforms_vbos[0]
        self.shared_program['transform_y'] = self._instance_transforms_vbos[1]
        self.shared_program['transform_z'] = self._instance_transforms_vbos[2]
        self.shared_program['shift'] = self._instance_positions_vbo

        self.events.data_updated()
