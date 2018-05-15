# -*- coding: utf-8 -*-

"""
Tests for texture-based colormap
All images are of size (100,100) to keep a small file size
"""

import numpy as np

from vispy.scene.visuals import Image
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved
from vispy.color import get_colormap
from vispy.color import Colormap
# import vispy.io as io

size = (100, 100)


@requires_application()
def test_colormap():
    """Test colormap support for non-uniformly distributed control-points"""
    with TestingCanvas(size=size, bgcolor='w') as c:
        idata = np.linspace(255, 0, size[0]*size[1]).astype(np.ubyte)
        data = idata.reshape((size[0], size[1]))
        image = Image(cmap=Colormap(colors=['k', 'w', 'r'],
                      controls=[0.0, 0.1, 1.0]),
                      clim='auto', parent=c.scene)
        image.set_data(data)
        assert_image_approved(c.render(), "visuals/colormap_kwr.png")
#        io.write_png("colormap_kwr.png", c.render())


@requires_application()
def test_colormap_single_hue():
    """Test colormap support using a single hue()"""
    with TestingCanvas(size=size, bgcolor='w') as c:
        idata = np.linspace(255, 0, size[0]*size[1]).astype(np.ubyte)
        data = idata.reshape((size[0], size[1]))
        image = Image(cmap=get_colormap('single_hue', 255),
                      clim='auto', parent=c.scene)
        image.set_data(data)
        assert_image_approved(c.render(), "visuals/colormap_single_hue.png")
#        io.write_png("colormap_single_hue.png", c.render())


@requires_application()
def test_colormap_coolwarm():
    """Test colormap support using coolwarm preset colormap"""
    with TestingCanvas(size=size, bgcolor='w') as c:
        idata = np.linspace(255, 0, size[0]*size[1]).astype(np.ubyte)
        data = idata.reshape((size[0], size[1]))
        image = Image(cmap='coolwarm', clim='auto', parent=c.scene)
        image.set_data(data)
        assert_image_approved(c.render(), "visuals/colormap_coolwarm.png")
#        io.write_png("colormap_coolwarm.png", c.render())


@requires_application()
def test_colormap_CubeHelix():
    """Test colormap support using cubehelix colormap in only blues"""
    with TestingCanvas(size=size, bgcolor='w') as c:
        idata = np.linspace(255, 0, size[0]*size[1]).astype(np.ubyte)
        data = idata.reshape((size[0], size[1]))
        image = Image(cmap=get_colormap('cubehelix', rot=0, start=0),
                      clim='auto', parent=c.scene)
        image.set_data(data)
        assert_image_approved(c.render(), "visuals/colormap_cubehelix.png")
#        io.write_png("colormap_cubehelix.png", c.render())


run_tests_if_main()
