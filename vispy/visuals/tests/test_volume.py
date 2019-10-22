# -*- coding: utf-8 -*-

import numpy as np
from vispy import scene

from vispy.testing import (TestingCanvas, requires_application,
                           run_tests_if_main, requires_pyopengl,
                           raises)
from vispy.testing.image_tester import assert_image_approved


@requires_pyopengl()
def test_volume():
    vol = np.zeros((20, 20, 20), 'float32')
    vol[8:16, 8:16, :] = 1.0
    
    # Create
    V = scene.visuals.Volume(vol)
    assert V.clim == (0, 1)
    assert V.method == 'mip'
    
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
