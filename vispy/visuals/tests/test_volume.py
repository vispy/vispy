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


run_tests_if_main()
