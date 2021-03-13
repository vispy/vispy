# -*- coding: utf-8 -*-
import numpy as np
from vispy.scene.visuals import Spheres
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved


@requires_application()
def test_spheres():
    """Test basic spheres support"""
    np.random.seed(57983)
    data = np.random.normal(size=(30, 3), loc=50, scale=10)
    
    with TestingCanvas() as c:
        spheres = Spheres(parent=c.scene)
        spheres.set_data(data)
        assert_image_approved(c.render(), "visuals/spheres.png")

    # Test good correlation at high-dpi
    with TestingCanvas(px_scale=2) as c:
        spheres = Spheres(parent=c.scene)
        spheres.set_data(data)
        assert_image_approved(c.render(), "visuals/spheres.png")


run_tests_if_main()
