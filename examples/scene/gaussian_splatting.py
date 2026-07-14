# -*- coding: utf-8 -*-
# vispy: testskip
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
3D Gaussian Splatting viewer
============================

Render a 3D Gaussian Splatting scene with the
:class:`~vispy.scene.visuals.GaussianSplat` visual.

This reads a ``.ply`` file in the layout emitted by the INRIA "3D Gaussian
Splatting for Real-Time Radiance Field Rendering" code and compatible tools
(x/y/z, f_dc_*, opacity, scale_*, rot_*), builds a 3D covariance per Gaussian
from the log-space scales and rotation quaternions, and hands the resulting
arrays to the ``GaussianSplat`` visual. With no argument it fetches a small
sample scene from the vispy demo-data repository.

Color uses only the spherical-harmonics DC term (``f_dc_*``); view-dependent
SH (``f_rest_*``) is ignored.

Requires the ``plyfile`` package (``pip install plyfile``).

Usage::

    python gaussian_splatting.py                          # fetch sample scene
    python gaussian_splatting.py path/to/point_cloud.ply --subsample 4
"""
import argparse
import sys

import numpy as np

from vispy import app, scene, use
from vispy.io import load_data_file

# Full gl+ context is required for instanced rendering.
use(gl='gl+')

# Default sample scene, fetched on demand from the vispy demo-data repo.
DEFAULT_PLY = 'gaussian_splatting/cluster/cluster_fly_S.ply'


def load_splats(path, subsample=1):
    """Read a 3DGS ply and return per-Gaussian arrays, normalized to a unit box.

    Returns ``(positions, covariances, colors)`` as float32 arrays with shapes
    (N, 3), (N, 3, 3) and (N, 4), where ``colors`` is RGBA (alpha is opacity).
    """
    from plyfile import PlyData

    v = PlyData.read(path).elements[0].data
    if subsample > 1:
        v = v[::subsample]

    xyz = np.stack([v['x'], v['y'], v['z']], axis=-1).astype(np.float64)

    # Normalize to a unit-ish box: keeps the shader's finite-difference step
    # scale-stable and frames the default camera regardless of source units.
    center = np.median(xyz, axis=0)
    xyz -= center
    radius = np.percentile(np.linalg.norm(xyz, axis=1), 95.0)
    scale_norm = radius if radius > 0 else 1.0
    xyz /= scale_norm

    # scale_* are log-space std-devs; rot_* is a (w, x, y, z) quaternion.
    scales = np.exp(np.stack([v[f'scale_{i}'] for i in range(3)], axis=-1))
    scales = scales.astype(np.float64) / scale_norm
    quats = np.stack([v[f'rot_{i}'] for i in range(4)], axis=-1).astype(np.float64)
    quats /= np.linalg.norm(quats, axis=1, keepdims=True) + 1e-9

    w, x, y, z = quats[:, 0], quats[:, 1], quats[:, 2], quats[:, 3]
    R = np.empty((len(quats), 3, 3))
    R[:, 0, 0] = 1 - 2 * (y * y + z * z)
    R[:, 0, 1] = 2 * (x * y - w * z)
    R[:, 0, 2] = 2 * (x * z + w * y)
    R[:, 1, 0] = 2 * (x * y + w * z)
    R[:, 1, 1] = 1 - 2 * (x * x + z * z)
    R[:, 1, 2] = 2 * (y * z - w * x)
    R[:, 2, 0] = 2 * (x * z - w * y)
    R[:, 2, 1] = 2 * (y * z + w * x)
    R[:, 2, 2] = 1 - 2 * (x * x + y * y)

    # Sigma = R S S^T R^T, with M = R @ diag(scales) so Sigma = M @ M^T.
    M = R * scales[:, None, :]
    sigma = np.einsum('nij,nkj->nik', M, M)

    # TODO: use only the SH DC term (f_dc_*) for now; view-dependent color
    # from the higher-order f_rest_* coefficients is discarded. Evaluating it
    # requires shader support in GaussianSplatVisual (see its docstring).
    SH_C0 = 0.28209479177387814  # degree-0 spherical harmonics constant
    rgb = 0.5 + SH_C0 * np.stack(
        [v['f_dc_0'], v['f_dc_1'], v['f_dc_2']], axis=-1
    )
    rgb = np.clip(rgb, 0.0, 1.0)
    opacity = 1.0 / (1.0 + np.exp(-v['opacity'].astype(np.float64)))
    rgba = np.concatenate([rgb, opacity[:, None]], axis=-1)

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
    parser.add_argument('--subsample', type=int, default=1,
                        help='keep every Nth splat (default 1 = all)')
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

    positions, covariances, colors = load_splats(path, args.subsample)
    print(f'loaded {len(positions):,} gaussians')

    canvas = scene.SceneCanvas(keys='interactive', show=True, bgcolor='black')
    view = canvas.central_widget.add_view()
    view.camera = scene.cameras.TurntableCamera(
        fov=45.0, distance=3.0, up=up)

    scene.visuals.GaussianSplat(positions, covariances, colors,
                                parent=view.scene)

    canvas.show()
    if sys.flags.interactive != 1:
        app.run()


if __name__ == '__main__':
    main()
