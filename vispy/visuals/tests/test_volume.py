# -*- coding: utf-8 -*-

import pytest
import numpy as np
from vispy import scene

from vispy.testing import (TestingCanvas, requires_application,
                           run_tests_if_main, requires_pyopengl,
                           raises)
from vispy.testing.image_tester import assert_image_approved, downsample
from vispy.testing.rendered_array_tester import compare_render, max_for_dtype


@requires_pyopengl()
def test_volume():
    vol = np.zeros((20, 20, 20), 'float32')
    vol[8:16, 8:16, :] = 1.0

    # Create
    V = scene.visuals.Volume(vol)
    assert V.clim == (0, 1)
    assert V.method == 'mip'
    assert V.interpolation == 'linear'

    # Set wrong data
    with raises(ValueError):
        V.set_data(np.zeros((20, 20), 'float32'))

    # Clim
    V.set_data(vol, (0.5, 0.8))
    assert V.clim == (0.5, 0.8)
    with raises(ValueError):
        V.set_data((0.5, 0.8, 1.0))

    # Method
    V.method = 'iso'
    assert V.method == 'iso'

    # Interpolation
    V.interpolation = 'nearest'
    assert V.interpolation == 'nearest'

    # Step size
    V.relative_step_size = 1.1
    assert V.relative_step_size == 1.1
    # Disallow 0 step size to avoid GPU stalling
    with raises(ValueError):
        V.relative_step_size = 0


@requires_pyopengl()
def test_volume_bounds():
    vol = np.zeros((20, 30, 40), 'float32')
    vol[8:16, 8:16, :] = 1.0

    # Create
    V = scene.visuals.Volume(vol)
    assert V._compute_bounds(0, V) == (0, 40)  # x
    assert V._compute_bounds(1, V) == (0, 30)  # y
    assert V._compute_bounds(2, V) == (0, 20)  # z


@requires_pyopengl()
@requires_application()
def test_volume_draw():
    with TestingCanvas(bgcolor='k', size=(100, 100)) as c:
        v = c.central_widget.add_view()
        v.camera = 'turntable'
        v.camera.fov = 70
        # Create
        np.random.seed(2376)
        vol = np.random.normal(size=(20, 20, 20), loc=0.5, scale=0.2)
        vol[8:16, 8:16, :] += 1.0
        scene.visuals.Volume(vol, parent=v.scene)  # noqa
        v.camera.set_range()
        assert_image_approved(c.render(), 'visuals/volume.png')


@requires_pyopengl()
@requires_application()
@pytest.mark.parametrize('clim_on_init', [False, True])
@pytest.mark.parametrize('texture_format', [None, '__dtype__', 'auto'])
@pytest.mark.parametrize('input_dtype', [np.uint8, np.uint16, np.float32, np.float64])
def test_volume_clims_and_gamma(texture_format, input_dtype, clim_on_init):
    """Test volume visual with clims and gamma on shader.

    Test is parameterized based on ``texture_format`` and should produce
    relatively the same results for each format.

    Currently just using np.ones since the angle of view made more complicated samples
    challenging, but this confirms gamma and clims works in the shader.
    The VolumeVisual defaults to the "grays" colormap so although we compare
    data using RGBA arrays, each R/G/B channel should be the same.

    """
    size = (40, 40)
    if texture_format == '__dtype__':
        texture_format = input_dtype
    np.random.seed(0)  # make tests the same every time
    data = _make_test_data(size[:1] * 3, input_dtype)
    clim = (0, 1)
    new_clim = (0.3, 0.8)
    max = max_for_dtype(input_dtype)
    if max != 1:
        clim = (clim[0] * max, clim[1] * max)
        new_clim = (new_clim[0] * max, new_clim[1] * max)

    kwargs = {}
    if clim_on_init:
        kwargs['clim'] = clim
    with TestingCanvas(size=size, bgcolor="k") as c:
        v = c.central_widget.add_view(border_width=0)
        volume = scene.visuals.Volume(
            data,
            interpolation='nearest',
            parent=v.scene,
            method='mip',
            texture_format=texture_format,
            **kwargs
        )
        v.camera = 'arcball'
        v.camera.fov = 0
        v.camera.scale_factor = 40.0
        v.camera.center = (19.5, 19.5, 19.5)

        rendered = c.render()
        _dtype = rendered.dtype
        shape_ratio = rendered.shape[0] // data.shape[0]
        rendered1 = downsample(rendered, shape_ratio, axis=(0, 1)).astype(_dtype)
        predicted = data.max(axis=1)
        compare_render(predicted, rendered1)

        # adjust contrast limits
        volume.clim = new_clim
        rendered2 = downsample(c.render(), shape_ratio, axis=(0, 1)).astype(_dtype)
        scaled_data = (np.clip(data, new_clim[0], new_clim[1]) - new_clim[0]) / (new_clim[1] - new_clim[0])
        predicted = scaled_data.max(axis=1)
        compare_render(predicted, rendered2, previous_render=rendered)

        # adjust gamma
        volume.gamma = 2
        rendered3 = downsample(c.render(), shape_ratio, axis=(0, 1)).astype(_dtype)
        predicted = (scaled_data ** 2).max(axis=1)
        compare_render(predicted, rendered3, previous_render=rendered2)


@requires_pyopengl()
@requires_application()
@pytest.mark.parametrize('method_name', scene.visuals.Volume._rendering_methods.keys())
def test_all_render_methods(method_name):
    """Test that render methods don't produce any errors."""
    size = (40, 40)
    np.random.seed(0)  # make tests the same every time
    data = _make_test_data(size[:1] * 3, np.float32)
    # modify the data for 'minip' method so that there is at least one segment
    # of the volume with no 'empty'/zero space
    data[:, :, 40 // 3: 2 * 40 // 3] = 1.0
    clim = (0, 1)
    kwargs = {}
    with TestingCanvas(size=size, bgcolor="k") as c:
        v = c.central_widget.add_view(border_width=0)
        volume = scene.visuals.Volume(
            data,
            interpolation='nearest',
            clim=clim,
            parent=v.scene,
            method=method_name,
            **kwargs
        )
        v.camera = 'arcball'
        v.camera.fov = 0
        v.camera.scale_factor = 40.0
        v.camera.center = (19.5, 19.5, 19.5)

        assert volume.method == method_name
        rendered = c.render()[..., :3]
        # not all black
        assert rendered.sum() != 0
        # not all white
        assert rendered.sum() != 255 * rendered.size


@requires_pyopengl()
@requires_application()
@pytest.mark.parametrize('texture_format', [None, 'auto'])
def test_equal_clims(texture_format):
    """Test that equal clims produce a min cmap value."""
    size = (40, 40)
    np.random.seed(0)  # make tests the same every time
    data = _make_test_data(size[:1] * 3, np.float32)
    with TestingCanvas(size=size, bgcolor="k") as c:
        v = c.central_widget.add_view(border_width=0)
        scene.visuals.Volume(
            data,
            interpolation='nearest',
            clim=(128.0, 128.0),  # equal clims
            cmap='viridis',  # something with a non-black min value
            parent=v.scene,
            method='mip',
            texture_format=texture_format,
        )
        v.camera = 'arcball'
        v.camera.fov = 0
        v.camera.scale_factor = 40.0
        v.camera.center = (19.5, 19.5, 19.5)

        rendered = c.render()[..., :3]
        # not all black
        assert rendered.sum() != 0
        # not all white
        assert rendered.sum() != 255 * rendered.size
        # should be all the same value
        r_unique = np.unique(rendered[..., 0])
        g_unique = np.unique(rendered[..., 1])
        b_unique = np.unique(rendered[..., 2])
        assert r_unique.size == 1
        assert g_unique.size == 1
        assert b_unique.size == 1


def _make_test_data(shape, input_dtype):
    one_third = shape[0] // 3
    two_third = 2 * one_third
    data = np.zeros(shape, dtype=np.float64)
    # 0.00 | 1.00 | 0.00
    # 0.50 | 0.00 | 0.25
    # 0.00 | 0.00 | 0.00
    data[:, :one_third, one_third:two_third] = 1.0
    data[:, one_third:two_third, :one_third] = 0.5
    data[:, one_third:two_third, two_third:] = 0.25
    max_val = max_for_dtype(input_dtype)
    if max_val != 1:
        data *= max_val
    data = data.astype(input_dtype)
    return data


@requires_pyopengl()
def test_set_data_does_not_change_input():
    # Create volume
    V = scene.visuals.Volume(np.zeros((20, 20, 20), dtype=np.float32))

    # calling Volume.set_data() should NOT alter the values of the input array
    # regardless of data type
    vol = np.random.randint(0, 200, (20, 20, 20))
    for dtype in ['uint8', 'int16', 'uint16', 'float32', 'float64']:
        vol_copy = np.array(vol, dtype=dtype, copy=True)
        # setting clim so that normalization would otherwise change the data
        V.set_data(vol_copy, clim=(0, 200))
        assert np.allclose(vol, vol_copy)

    # dtype has to be the same as the one used to init the texture, or it will
    # be first coerced to the same dtype as the init

    vol2 = np.array(vol, dtype=np.float32, copy=True)
    assert np.allclose(vol, vol2)
    # we explicitly create a copy when data would be altered by the texture,
    # no matter what the user asks, so the data outside should never change
    V.set_data(vol2, clim=(0, 200), copy=False)
    assert np.allclose(vol, vol2)


@requires_pyopengl()
def test_set_data_changes_shape():
    dtype = np.float32
    # Create initial volume
    V = scene.visuals.Volume(np.zeros((20, 20, 20), dtype=dtype))

    # Sending new three dimensional data of different shape should alter volume shape
    vol = np.zeros((25, 25, 10), dtype=dtype)
    V.set_data(vol)
    assert V._vol_shape == (25, 25, 10)

    # Sending data of dimension other than 3 should raise a ValueError
    vol2 = np.zeros((20, 20), dtype=dtype)
    with pytest.raises(ValueError):
        V.set_data(vol2)

    vol2 = np.zeros((20, 20, 20, 20), dtype=dtype)
    with pytest.raises(ValueError):
        V.set_data(vol2)


@requires_pyopengl()
@requires_application()
def test_changing_cmap():
    """Test that changing colormaps updates the display."""
    size = (40, 40)
    np.random.seed(0)  # make tests the same every time
    data = _make_test_data(size[:1] * 3, np.float32)
    cmap = 'grays'
    test_cmaps = ('reds', 'greens', 'blues')
    clim = (0, 1)
    kwargs = {}
    with TestingCanvas(size=size, bgcolor="k") as c:
        v = c.central_widget.add_view(border_width=0)
        volume = scene.visuals.Volume(
            data,
            interpolation='nearest',
            clim=clim,
            cmap=cmap,
            parent=v.scene,
            **kwargs
        )
        v.camera = 'arcball'
        v.camera.fov = 0
        v.camera.scale_factor = 40.0

        # render with grays colormap
        grays = c.render()

        # update cmap, compare rendered array with the grays cmap render
        for cmap in test_cmaps:
            volume.cmap = cmap
            current_cmap = c.render()
            with pytest.raises(AssertionError):
                np.testing.assert_allclose(grays, current_cmap)


@requires_pyopengl()
@requires_application()
def test_plane_depth():
    with TestingCanvas(size=(80, 80)) as c:
        v = c.central_widget.add_view(border_width=0)
        v.camera = 'arcball'
        v.camera.fov = 0
        v.camera.center = (40, 40, 40)
        v.camera.scale_factor = 80.0

        # two planes at 45 degrees relative to the camera. If depth is set correctly, we should see one half
        # of the screen red and the other half white
        scene.visuals.Volume(
            np.ones((80, 80, 80), dtype=np.uint8),
            interpolation="nearest",
            clim=(0, 1),
            cmap="grays",
            raycasting_mode="plane",
            plane_normal=(0, 1, 1),
            parent=v.scene,
        )

        scene.visuals.Volume(
            np.ones((80, 80, 80), dtype=np.uint8),
            interpolation="nearest",
            clim=(0, 1),
            cmap="reds",
            raycasting_mode="plane",
            plane_normal=(0, 1, -1),
            parent=v.scene,
        )

        # render with grays colormap
        rendered = c.render()
        left = rendered[40, 20]
        right = rendered[40, 60]
        assert np.array_equal(left, [255, 0, 0, 255])
        assert np.array_equal(right, [255, 255, 255, 255])


@requires_pyopengl()
@requires_application()
def test_volume_depth():
    """Check that depth setting is properly performed for the volume visual

    Render a volume with a blue ball in front of a red plane in front of a
    blue plane, checking that the output image contains both red and blue pixels.
    """
    # A blue strip behind a red strip
    # If depth is set correctly, we should see only red pixels
    # the screen
    blue_vol = np.zeros((80, 80, 80), dtype=np.uint8)
    blue_vol[:, -1, :] = 1  # back plane blue
    blue_vol[30:50, 30:50, 30:50] = 1  # blue in center

    red_vol = np.zeros((80, 80, 80), dtype=np.uint8)
    red_vol[:, -5, :] = 1  # red plane in front of blue plane

    with TestingCanvas(size=(80, 80)) as c:
        v = c.central_widget.add_view(border_width=0)
        v.camera = 'arcball'
        v.camera.fov = 0
        v.camera.center = (40, 40, 40)
        v.camera.scale_factor = 80.0

        scene.visuals.Volume(
            red_vol,
            interpolation="nearest",
            clim=(0, 1),
            cmap="reds",
            parent=v.scene,
        )

        scene.visuals.Volume(
            blue_vol,
            interpolation="nearest",
            clim=(0, 1),
            cmap="blues",
            parent=v.scene,
        )

        # render
        rendered = c.render()
        reds = np.sum(rendered[:, :, 0])
        greens = np.sum(rendered[:, :, 1])
        blues = np.sum(rendered[:, :, 2])
        assert reds > 0
        np.testing.assert_allclose(greens, 0)
        assert blues > 0


@requires_pyopengl()
@requires_application()
def test_mip_cutoff():
    """
    Ensure fragments are properly discarded based on the mip_cutoff
    for the mip and attenuated_mip rendering methods
    """
    with TestingCanvas(size=(80, 80)) as c:
        v = c.central_widget.add_view(border_width=0)
        v.camera = 'arcball'
        v.camera.fov = 0
        v.camera.center = (40, 40, 40)
        v.camera.scale_factor = 80.0

        vol = scene.visuals.Volume(
            np.ones((80, 80, 80), dtype=np.uint8),
            interpolation="nearest",
            clim=(0, 1),
            cmap="grays",
            parent=v.scene,
        )

        # we should see white
        rendered = c.render()
        assert np.array_equal(rendered[40, 40], [255, 255, 255, 255])

        vol.mip_cutoff = 10
        # we should see black
        rendered = c.render()
        assert np.array_equal(rendered[40, 40], [0, 0, 0, 255])

        # repeat for attenuated_mip
        vol.method = 'attenuated_mip'
        vol.mip_cutoff = None

        # we should see white
        rendered = c.render()
        assert np.array_equal(rendered[40, 40], [255, 255, 255, 255])

        vol.mip_cutoff = 10
        # we should see black
        rendered = c.render()
        assert np.array_equal(rendered[40, 40], [0, 0, 0, 255])


@requires_pyopengl()
@requires_application()
def test_minip_cutoff():
    """
    Ensure fragments are properly discarded based on the minip_cutoff
    for the minip rendering method
    """
    with TestingCanvas(size=(80, 80)) as c:
        v = c.central_widget.add_view(border_width=0)
        v.camera = 'arcball'
        v.camera.fov = 0
        v.camera.center = (40, 40, 40)
        v.camera.scale_factor = 120.0

        # just surface of the cube is ones, but it should win over the twos inside
        data = np.ones((80, 80, 80), dtype=np.uint8)
        data[1:-1, 1:-1, 1:-1] = 2

        vol = scene.visuals.Volume(
            data,
            interpolation="nearest",
            method='minip',
            clim=(0, 2),
            cmap="grays",
            parent=v.scene,
        )

        # we should see gray (half of cmap)
        rendered = c.render()
        assert np.array_equal(rendered[40, 40], [128, 128, 128, 255])

        # discard fragments above -10 (everything)
        vol.minip_cutoff = -10
        # we should see black
        rendered = c.render()
        assert np.array_equal(rendered[40, 40], [0, 0, 0, 255])


@requires_pyopengl()
@requires_application()
def test_volume_set_data_different_dtype():
    size = (80, 80)
    data = np.array([[[0, 127]]], dtype=np.int8)
    left = (40, 10)
    right = (40, 70)
    white = (255, 255, 255, 255)
    black = (0, 0, 0, 255)

    with TestingCanvas(size=size[::-1], bgcolor="w") as c:
        view = c.central_widget.add_view()
        view.camera = 'arcball'
        view.camera.fov = 0
        view.camera.center = 0.5, 0, 0
        view.camera.scale_factor = 2
        volume = scene.visuals.Volume(
            data,
            cmap='grays',
            clim=[0, 127],
            parent=view.scene
        )

        render = c.render()
        assert np.allclose(render[left], black)
        assert np.allclose(render[right], white)

        # same data as float should change nothing
        volume.set_data(data.astype(np.float32))
        render = c.render()
        assert np.allclose(render[left], black)
        assert np.allclose(render[right], white)

        # something inverted, different dtype
        new_data = np.array([[[127, 0]]], dtype=np.float16)
        volume.set_data(new_data)
        render = c.render()
        assert np.allclose(render[left], white)
        assert np.allclose(render[right], black)

        # out of bounds should clip (2000 > 127)
        new_data = np.array([[[0, 2000]]], dtype=np.float64)
        volume.set_data(new_data)
        render = c.render()
        assert np.allclose(render[left], black)
        assert np.allclose(render[right], white)


run_tests_if_main()
