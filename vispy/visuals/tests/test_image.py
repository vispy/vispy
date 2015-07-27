# -*- coding: utf-8 -*-
import numpy as np

from vispy.scene.visuals import Image
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved


@requires_application()
def test_image():
    """Test image visual"""
    size = (100, 50)
    with TestingCanvas(size=size, bgcolor='w') as c:
        image = Image(cmap='grays', clim=[0, 1], parent=c.scene)
        for three_d in (True, False):
            shape = (size[1]-10, size[0]-10) + ((3,) if three_d else ())
            np.random.seed(379823)
            data = np.random.rand(*shape)
            image.set_data(data)
            assert_image_approved(c.render(), "visuals/image%s.png" %
                                  ("_rgb" if three_d else "_mono"))


run_tests_if_main()
