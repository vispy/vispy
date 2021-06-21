# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from vispy.app import Canvas
from vispy.visuals import ImageVisual
from vispy.testing import requires_application


@requires_application()
def test_run():
    """Test app running"""
    with Canvas(size=(100, 100), show=True, title='run') as c:

        image = Image(cmap='grays', clim=[0, 1], parent=c.scene)
        shape = (size[1]-10, size[0]-10) + ((3,) if is_3d else ())
        np.random.seed(379823)
        data = np.random.rand(*shape)
        image.set_data(data)
        assert_image_approved(c.render(), "visuals/image%s.png" %
                              ("_rgb" if is_3d else "_mono"))
