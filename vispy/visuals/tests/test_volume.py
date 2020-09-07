# -*- coding: utf-8 -*-

import numpy as np
from vispy import scene

from vispy.testing import (TestingCanvas, requires_application,
                           run_tests_if_main, requires_pyopengl,
                           raises)
from vispy.testing.image_tester import assert_image_approved, downsample


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
def test_volume_clims_and_gamma():
    """Test volume visual with clims and gamma on shader.
    
    currently just using np.ones since the angle of view made more complicated samples
    challenging, but this confirms gamma and clims works in the shader.
    """

    with TestingCanvas(size=(40, 40), bgcolor="k") as c:
        v = c.central_widget.add_view(border_width=0, size=(40, 40))
        data = np.ones((40, 40, 40)) / 2.5
        volume = scene.visuals.Volume(
            data,
            clim=(0, 1),
            interpolation='nearest',
            parent=v.scene,
            method='mip',
        )
        v.camera = 'arcball'
        v.camera.fov = 0
        v.camera.scale_factor = 40
        v.camera.center = (19.5, 19.5, 19.5)

        rendered = c.render()[..., 0]
        _dtype = rendered.dtype
        shape_ratio = rendered.shape[0] // data.shape[0]
        rendered1 = downsample(rendered, shape_ratio, axis=(0, 1)).astype(_dtype)
        predicted = np.round(data.max(0) * 255).astype(np.uint8)
        assert np.allclose(predicted, rendered1, atol=1)

        # adjust contrast limits
        new_clim = (0.3, 0.8)
        volume.clim = new_clim
        rendered2 = downsample(c.render()[..., 0], shape_ratio, axis=(0, 1)).astype(_dtype)
        scaled_data = np.clip((data - new_clim[0]) / np.diff(new_clim)[0], 0, 1)
        predicted = np.round(scaled_data.max(0) * 255).astype(np.uint8)
        assert np.allclose(predicted, rendered2)
        assert not np.allclose(rendered1, rendered2, atol=10)

        # adjust gamma
        volume.gamma = 1.5
        rendered3 = downsample(c.render()[..., 0], shape_ratio, axis=(0, 1)).astype(_dtype)
        predicted = np.round((scaled_data ** volume.gamma).max(0) * 255).astype(np.uint8)
        assert np.allclose(predicted, rendered3)
        assert not np.allclose(rendered2, rendered3, atol=10)


@requires_pyopengl()
def test_set_data_does_not_change_input():
    # Create volume
    V = scene.visuals.Volume(np.zeros((20, 20, 20)))

    # calling Volume.set_data() should NOT alter the values of the input array
    # regardless of data type
    vol = np.random.randint(0, 200, (20, 20, 20))
    for dtype in ['uint8', 'int16', 'uint16', 'float32', 'float64']:
        vol_copy = np.array(vol, dtype=dtype, copy=True)
        # setting clim so that normalization would otherwise change the data
        V.set_data(vol_copy, clim=(0, 200))
        assert np.allclose(vol, vol_copy)

    # for those using float32 who want to avoid the copy operation,
    # using set_data() with `copy=False` should be expected to alter the data.
    vol2 = np.array(vol, dtype='float32', copy=True)
    assert np.allclose(vol, vol2)
    V.set_data(vol2, clim=(0, 200), copy=False)
    assert not np.allclose(vol, vol2)


run_tests_if_main()
