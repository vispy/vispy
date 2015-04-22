# -*- coding: utf-8 -*-

import numpy as np
from vispy import scene

from vispy.testing import run_tests_if_main, requires_pyopengl
from vispy.testing import (TestingCanvas, requires_application, 
                           assert_image_approved)
#from vispy.gloo.util import _screenshot
from nose.tools import assert_raises


@requires_pyopengl()
def test_volume():
    
    vol = np.zeros((20, 20, 20), 'float32')
    vol[8:16, 8:16, :] = 1.0
    
    # Create
    V = scene.visuals.Volume(vol)
    assert V.clim == (0, 1)
    assert V.method == 'mip'
    
    # Set wrong data
    assert_raises(ValueError, V.set_data, np.zeros((20, 20), 'float32'))
    
    # Clim
    V.set_data(vol, (0.5, 0.8))
    assert V.clim == (0.5, 0.8)
    assert_raises(ValueError, V.set_data, vol, (0.5, 0.8, 1.0))
    
    # Method
    V.method = 'iso'
    assert V.method == 'iso'
    
    # Step size
    V.relative_step_size = 1.1
    assert V.relative_step_size == 1.1
    # Disallow 0 step size to avoid GPU stalling
    assert_raises(ValueError, V.__class__.relative_step_size.fset, V, 0)


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
        #vol = np.zeros((20, 20, 20), dtype='float32')
        vol[8:16, 8:16, :] += 1.0
        V = scene.visuals.Volume(vol, parent=v.scene)
        #V.transform = scene.STTransform(scale=(2, 2, 1),
                                        #translate=(50, 50, 0))
        #c.draw_visual(V)
        v.camera.set_range()
        assert_image_approved(c.render(), 'visuals/volume.png')


run_tests_if_main()
