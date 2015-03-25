# -*- coding: utf-8 -*-

import numpy as np
from vispy.scene.visuals import Volume

from vispy.testing import run_tests_if_main, requires_pyopengl
from vispy.testing import TestingCanvas, requires_application
#from vispy.gloo.util import _screenshot
from nose.tools import assert_raises


@requires_pyopengl()
def test_volume():
    
    vol = np.zeros((20, 20, 20), 'float32')
    vol[8:16, 8:16, :] = 1.0
    
    # Create
    V = Volume(vol)
    assert V.clim == (0, 1)
    assert V.style == 'mip'
    
    # Set wrong data
    assert_raises(ValueError, V.set_data, np.zeros((20, 20), 'float32'))
    
    # Clim
    V.set_data(vol, (0.5, 0.8))
    assert V.clim == (0.5, 0.8)
    assert_raises(ValueError, V.set_data, vol, (0.5, 0.8, 1.0))
    
    # Style
    V.style = 'iso'
    assert V.style == 'iso'
    
    # Step size
    V.relative_step_size = 1.1
    assert V.relative_step_size == 1.1
    # Disallow 0 step size to avoid GPU stalling
    assert_raises(ValueError, V.__class__.relative_step_size.fset, V, 0)


@requires_pyopengl()
@requires_application()
def test_volume_draw():
    with TestingCanvas(bgcolor='w', size=(92, 92)) as c:
        # Create
        vol = np.zeros((20, 20, 20), 'float32')
        vol[8:16, 8:16, :] = 1.0
        V = Volume(vol)
        c.draw_visual(V)
        
        # If the draw went without errors, we are happy for the test ...


run_tests_if_main()
