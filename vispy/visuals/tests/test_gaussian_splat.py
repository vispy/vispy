# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""Tests for GaussianSplatVisual."""

import numpy as np
import pytest

from vispy import scene, use, visuals
from vispy.testing import (TestingCanvas, has_pyopengl, requires_application,
                           requires_pyopengl, run_tests_if_main)


# the data-only tests don't need gl+, so only switch when PyOpenGL is around;
# the drawing tests are marked requires_pyopengl
def setup_module(module):
    if has_pyopengl():
        use(gl='gl+')


def teardown_module(module):
    if has_pyopengl():
        use(gl='gl2')


def _make_splats(n=50, seed=0):
    rng = np.random.RandomState(seed)
    positions = rng.randn(n, 3).astype(np.float32)
    a = (rng.randn(n, 3, 3) * 0.1).astype(np.float32)
    # symmetric positive-definite covariances
    covariances = np.einsum('nij,nkj->nik', a, a) + np.eye(3, dtype=np.float32) * 0.02
    colors = rng.rand(n, 4).astype(np.float32)  # RGBA
    return positions, covariances, colors


def test_splat_data_roundtrip():
    positions, covariances, colors = _make_splats()
    v = visuals.GaussianSplatVisual(positions, covariances, colors)

    np.testing.assert_array_equal(v.positions, positions)
    np.testing.assert_allclose(v.colors, colors, atol=1e-6)
    np.testing.assert_allclose(v.opacities, colors[:, 3], atol=1e-6)
    # covariances are packed to the triangle and reassembled symmetrically
    np.testing.assert_allclose(v.covariances, covariances, atol=1e-6)
    assert np.allclose(v.covariances, np.transpose(v.covariances, (0, 2, 1)))


def test_splat_compute_bounds():
    positions, covariances, colors = _make_splats()
    v = visuals.GaussianSplatVisual(positions, covariances, colors)
    for axis in range(3):
        lo, hi = v._compute_bounds(axis, None)
        assert lo == positions[:, axis].min()
        assert hi == positions[:, axis].max()


def test_splat_set_data_partial():
    positions, covariances, colors = _make_splats()
    v = visuals.GaussianSplatVisual(positions, covariances, colors)
    v.set_data(colors=np.clip(colors * 0.5, 0, 1))
    np.testing.assert_allclose(v.colors, np.clip(colors * 0.5, 0, 1), atol=1e-6)
    # untouched arrays are preserved
    np.testing.assert_array_equal(v.positions, positions)


def test_splat_eps():
    positions, covariances, colors = _make_splats()
    # the finite-difference step is ~1% of the bounding-box extent
    v = visuals.GaussianSplatVisual(positions, covariances, colors)
    extent = float((positions.max(0) - positions.min(0)).max())
    assert np.isclose(v.shared_program['u_eps'], 1e-2 * extent)
    # scaling the scene scales the step proportionally (numerically stable)
    v2 = visuals.GaussianSplatVisual(positions * 1000, covariances, colors)
    assert np.isclose(v2.shared_program['u_eps'], 1e-2 * extent * 1000)


def test_splat_rgb_plus_opacities():
    """(N, 3) RGB works as long as opacities is supplied separately."""
    positions, covariances, colors = _make_splats(10)
    v = visuals.GaussianSplatVisual(positions, covariances, colors[:, :3],
                                    opacities=colors[:, 3])
    np.testing.assert_allclose(v.colors, colors, atol=1e-6)

    # a scalar opacity broadcasts over all splats
    v = visuals.GaussianSplatVisual(positions, covariances, colors[:, :3],
                                    opacities=0.25)
    np.testing.assert_array_equal(v.opacities, np.full(10, 0.25, np.float32))


def test_splat_single_color_broadcast():
    """A single color applies to every splat (useful for debugging)."""
    positions, covariances, _ = _make_splats(10)

    v = visuals.GaussianSplatVisual(positions, covariances, 'white',
                                    opacities=0.3)
    np.testing.assert_allclose(v.colors, np.tile([1, 1, 1, 0.3], (10, 1)),
                               atol=1e-6)

    # a color may carry its own alpha, which opacities then overrides
    v = visuals.GaussianSplatVisual(positions, covariances, '#ff000080')
    np.testing.assert_allclose(v.colors[:, :3], np.tile([1, 0, 0], (10, 1)),
                               atol=1e-6)
    np.testing.assert_allclose(v.colors[:, 3], 0.5019608, atol=1e-6)

    v = visuals.GaussianSplatVisual(positions, covariances, (0, 0, 1, 0.25),
                                    opacities=0.9)
    np.testing.assert_allclose(v.colors[:, 3], 0.9, atol=1e-6)

    # and it can replace per-splat colors after the fact
    v.set_data(colors=(0, 1, 0))
    np.testing.assert_allclose(v.colors[:, :3], np.tile([0, 1, 0], (10, 1)),
                               atol=1e-6)


def test_splat_opacities_conflicts_with_rgba():
    positions, covariances, colors = _make_splats(10)
    with pytest.raises(ValueError, match="alpha channel"):
        visuals.GaussianSplatVisual(positions, covariances, colors,
                                    opacities=np.ones(10, np.float32))


def test_splat_opacities_required():
    positions, covariances, colors = _make_splats(10)
    with pytest.raises(ValueError, match="opacities is required"):
        visuals.GaussianSplatVisual(positions, covariances, colors[:, :3])


def test_splat_bad_shapes():
    positions, covariances, colors = _make_splats()
    with pytest.raises(ValueError):
        visuals.GaussianSplatVisual(positions[:, :2], covariances, colors)
    with pytest.raises(ValueError):
        visuals.GaussianSplatVisual(positions, covariances[:, 0], colors)
    with pytest.raises(ValueError):
        # (N, 2) is neither RGB nor RGBA
        visuals.GaussianSplatVisual(positions, covariances, colors[:, :2],
                                    opacities=1.0)
    with pytest.raises(ValueError):
        visuals.GaussianSplatVisual(positions, covariances, 'notacolor',
                                    opacities=1.0)


def test_splat_values_out_of_range():
    positions, covariances, colors = _make_splats()
    bad = colors.copy()
    bad[0, 0] = 1.5
    with pytest.raises(ValueError, match="between 0 and 1"):
        visuals.GaussianSplatVisual(positions, covariances, bad)
    bad = colors[:, :3].copy()
    bad[0, 0] = -0.1
    with pytest.raises(ValueError, match="between 0 and 1"):
        visuals.GaussianSplatVisual(positions, covariances, bad, opacities=1.0)
    with pytest.raises(ValueError, match="between 0 and 1"):
        visuals.GaussianSplatVisual(positions, covariances, colors[:, :3],
                                    opacities=2.0)


def test_splat_mismatched_lengths():
    positions, covariances, colors = _make_splats(10)
    with pytest.raises(ValueError, match="length"):
        visuals.GaussianSplatVisual(positions, covariances, colors[:5])


def test_splat_empty():
    """An empty visual constructs and contributes no bounds."""
    v = visuals.GaussianSplatVisual(np.zeros((0, 3), np.float32),
                                    np.zeros((0, 3, 3), np.float32),
                                    np.zeros((0, 4), np.float32))
    assert v._compute_bounds(0, None) is None


def test_splat_failed_pack_leaves_visual_unchanged():
    """An error while packing must not half-apply the update."""
    import vispy.visuals.gaussian_splat as gsm

    positions, covariances, colors = _make_splats(20)
    v = visuals.GaussianSplatVisual(positions, covariances, colors)
    before = (v._splat_pos, v._splat_rgb, v._splat_alpha, v._bounds.copy())

    real = gsm.GaussianSplatVisual._pack_texture

    def boom(*args):
        raise ValueError("simulated pack failure")

    gsm.GaussianSplatVisual._pack_texture = staticmethod(boom)
    try:
        with pytest.raises(ValueError, match="simulated"):
            v.set_data(positions=positions * 3)
    finally:
        gsm.GaussianSplatVisual._pack_texture = staticmethod(real)

    assert v._splat_pos is before[0]
    assert v._splat_rgb is before[1]
    assert v._splat_alpha is before[2]
    np.testing.assert_array_equal(v._bounds, before[3])


def test_splat_capacity_message():
    """Too many splats is a ValueError explaining where the limit comes from."""
    from vispy.visuals.gaussian_splat import (
        _MAX_SPLATS, _MAX_TEX_HEIGHT, _SPLATS_PER_ROW)

    # the (column, row) slot upload lifted the old float32-index ceiling
    assert _MAX_SPLATS == _SPLATS_PER_ROW * _MAX_TEX_HEIGHT > 2 ** 24

    v = visuals.GaussianSplatVisual(*_make_splats(4))
    with pytest.raises(ValueError) as excinfo:
        v._pack_texture(np.zeros((_MAX_SPLATS + 1, 3), np.float32),
                        None, None, None, None)
    message = str(excinfo.value)
    assert f"{_MAX_SPLATS + 1:,}" in message
    assert f"{_MAX_SPLATS:,}" in message


def test_splat_opacities_not_shadowed_by_node():
    """`Node.opacity` is a whole-visual alpha and must not shadow ours."""
    positions, covariances, colors = _make_splats(10)
    splat = scene.visuals.GaussianSplat(positions, covariances, colors)
    np.testing.assert_allclose(splat.opacities, colors[:, 3], atol=1e-6)
    assert splat.opacity == 1.0


def test_splat_antialias_property():
    positions, covariances, colors = _make_splats()
    v = visuals.GaussianSplatVisual(positions, covariances, colors)
    assert v.antialias is False
    assert v.shared_program["u_antialias"] == 0.0

    v = visuals.GaussianSplatVisual(positions, covariances, colors,
                                    antialias=True)
    assert v.antialias is True
    assert v.shared_program["u_antialias"] == 1.0
    v.antialias = False
    assert v.shared_program["u_antialias"] == 0.0


@requires_pyopengl()
@requires_application()
def test_splat_draw():
    """A single opaque splat should paint pixels near the screen center."""
    with TestingCanvas(size=(100, 100), bgcolor='black') as c:
        use(gl='gl+')
        positions = np.array([[0, 0, 0]], dtype=np.float32)
        covariances = (np.eye(3, dtype=np.float32) * 0.1)[np.newaxis]
        colors = np.array([[1, 1, 1, 1]], dtype=np.float32)  # opaque white

        view = c.central_widget.add_view()
        view.camera = scene.cameras.TurntableCamera(fov=0, distance=3.0)
        scene.visuals.GaussianSplat(positions, covariances, colors,
                                    parent=view.scene)
        render = c.render()
        # something was drawn on the (otherwise black) canvas
        assert render[..., :3].sum() > 0


@requires_pyopengl()
@requires_application()
def test_splat_draw_antialias_dims_small_splats():
    """Compensating for the dilation lowers the opacity of a small splat."""
    positions = np.array([[0, 0, 0]], dtype=np.float32)
    # about a pixel across, so the dilation roughly doubles its area
    covariances = (np.eye(3, dtype=np.float32) * 1e-5)[np.newaxis]
    colors = np.array([[1, 1, 1, 1]], dtype=np.float32)
    with TestingCanvas(size=(100, 100), bgcolor='black') as c:
        use(gl='gl+')
        view = c.central_widget.add_view()
        view.camera = scene.cameras.TurntableCamera(fov=0, distance=3.0)
        splat = scene.visuals.GaussianSplat(positions, covariances, colors,
                                            parent=view.scene)
        plain = c.render()[..., :3].astype(float).sum()
        splat.antialias = True
        compensated = c.render()[..., :3].astype(float).sum()
    assert plain > 0
    assert 0 < compensated < plain


@requires_pyopengl()
@requires_application()
def test_splat_slots_address_every_splat():
    """The uploaded draw order names each splat's (column, row) texture slot."""
    from vispy.visuals.gaussian_splat import _SPLATS_PER_ROW

    n = 200
    positions, covariances, colors = _make_splats(n)
    with TestingCanvas(size=(100, 100), bgcolor='black') as c:
        use(gl='gl+')
        view = c.central_widget.add_view()
        view.camera = scene.cameras.TurntableCamera(fov=45)
        splat = scene.visuals.GaussianSplat(positions, covariances, colors,
                                            parent=view.scene)
        view.camera.set_range()

        uploaded = []
        splat._slot_vbo.set_data = lambda a, **kw: uploaded.append(a)
        splat._last_view_dir = None
        c.render()

        slots = uploaded[-1]
        assert slots.shape == (n, 2)
        # every splat appears exactly once, and each slot decodes to its index
        order = (slots[:, 1] * _SPLATS_PER_ROW + slots[:, 0]).astype(np.int64)
        np.testing.assert_array_equal(np.sort(order), np.arange(n))


@requires_pyopengl()
@requires_application()
def test_splat_resort_gating():
    """The depth sort re-runs on rotation but skips pan/zoom/static redraws."""
    positions, covariances, colors = _make_splats()
    with TestingCanvas(size=(100, 100), bgcolor='black') as c:
        use(gl='gl+')
        view = c.central_widget.add_view()
        view.camera = scene.cameras.TurntableCamera(fov=45)
        splat = scene.visuals.GaussianSplat(positions, covariances, colors,
                                            parent=view.scene)
        view.camera.set_range()

        c.render()
        view_dir = splat._last_view_dir.copy()
        assert view_dir is not None

        # static redraw, zoom and pan don't change the back-to-front order
        c.render()
        assert np.array_equal(view_dir, splat._last_view_dir)
        view.camera.scale_factor *= 0.5
        c.render()
        assert np.array_equal(view_dir, splat._last_view_dir)
        view.camera.center = (0.3, 0.0, 0.0)
        c.render()
        assert np.array_equal(view_dir, splat._last_view_dir)

        # a large rotation triggers a re-sort
        view.camera.azimuth += 20.0
        c.render()
        assert not np.array_equal(view_dir, splat._last_view_dir)


run_tests_if_main()
