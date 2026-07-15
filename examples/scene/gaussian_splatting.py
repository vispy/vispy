# -*- coding: utf-8 -*-
# vispy: testskip
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
3D Gaussian Splatting
=====================

Render a 3D Gaussian Splatting scene with the
:class:`~vispy.scene.visuals.GaussianSplat` visual.

This reads a ``.ply`` file in the layout emitted by the INRIA "3D Gaussian
Splatting for Real-Time Radiance Field Rendering" code and compatible tools
(x/y/z, f_dc_*, opacity, scale_*, rot_*), builds a 3D covariance per Gaussian
from the log-space scales and rotation quaternions, and hands the resulting
arrays to the ``GaussianSplat`` visual.

With no ply file provided this script fetches a sample file of a clusterfly
from the vispy demo-data repository. This file was orignally created by Dany
Bittel and retrieved from https://superspl.at/scene/285082b2 (licensed CC-BY).

Requires the ``plyfile`` and ``scipy`` packages
(``pip install plyfile scipy``).

Usage::

    python gaussian_splatting.py
    python gaussian_splatting.py path/to/point_cloud.ply
"""
import argparse
import sys

import numpy as np

from vispy import app, scene, use
from vispy.io import load_data_file

# Full gl+ context is required for instanced rendering.
use(gl='gl+')

DEFAULT_PLY = 'gaussian_splatting/cluster/cluster_fly_S.ply'


def load_splats(path):
    """Read a 3DGS ply and return per-Gaussian arrays compatible with
    the GaussianSplat visual.

    Returns ``(positions, covariances, colors)`` as float32 arrays with shapes
    (N, 3), (N, 3, 3) and (N, 4), where ``colors`` is RGBA (alpha is opacity).
    """
    from plyfile import PlyData
    from scipy.spatial.transform import Rotation

    v = PlyData.read(path).elements[0].data

    xyz = np.stack([v['x'], v['y'], v['z']], axis=-1).astype(np.float64)

    # scale_* are log-space std-devs
    scales = np.exp(np.stack([v[f'scale_{i}'] for i in range(3)], axis=-1))
    scales = scales.astype(np.float64)

    # rot_* is a (w, x, y, z) quaternion
    quats = np.stack([v[f'rot_{i}'] for i in range(4)], axis=-1)
    # scipy uses scalar-last (x, y, z, w) order and normalizes internally
    R = Rotation.from_quat(quats[:, [1, 2, 3, 0]]).as_matrix()

    # Sigma = R S S^T R^T
    # M = R @ diag(scales), so
    # Sigma = M @ M^T
    M = R * scales[:, None, :]
    # for each splat (row), do M @ M.T
    sigma = M @ M.swapaxes(-1, -2)

    # use only the DC term (f_dc_*) of the spherical harmonic colors
    # view-dependent color from the higher-order f_rest_* coefficients is
    # not supported by the GaussianSplat visual at this time
    SH_C0 = 1 / (2 * np.sqrt(np.pi))  # degree-0 spherical harmonics constant
    rgb = 0.5 + SH_C0 * np.stack(
        [v['f_dc_0'], v['f_dc_1'], v['f_dc_2']], axis=-1
    )
    rgb = np.clip(rgb, 0.0, 1.0)
    alpha = 1.0 / (1.0 + np.exp(-v['opacity'].astype(np.float64)))
    rgba = np.concatenate([rgb, alpha[:, None]], axis=-1)

    f32 = np.float32
    return (
        np.ascontiguousarray(xyz, f32),
        np.ascontiguousarray(sigma, f32),
        np.ascontiguousarray(rgba, f32),
    )


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('ply', nargs='?', default=None,
                        help='path to a 3DGS point_cloud.ply '
                             '(default fetches a sample)')
    parser.add_argument('--up', default='+z',
                        choices=['+x', '-x', '+y', '-y', '+z', '-z'],
                        help="scene up-axis. If the scene is upside down use "
                             "--up=-z; note negative axes need the '=' form. "
                             "Then try +y/-y (default +z)")
    args = parser.parse_args()

    if args.ply is not None:
        path = args.ply
        up = args.up
    else:
        path = load_data_file(DEFAULT_PLY)
        up = "-y"

    positions, covariances, colors = load_splats(path)
    print(f'loaded {len(positions):,} gaussians')

    canvas = scene.SceneCanvas(keys='interactive', show=True, bgcolor='black')
    view = canvas.central_widget.add_view()
    view.camera = scene.cameras.TurntableCamera(fov=45.0, up=up)

    scene.visuals.GaussianSplat(positions, covariances, colors,
                                parent=view.scene)
    view.camera.set_range()

    canvas.show()
    if sys.flags.interactive != 1:
        app.run()


if __name__ == '__main__':
    main()
