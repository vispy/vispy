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
from vispy.color import Colormap

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


@requires_application()
def test_colormap_discrete():
    """Test discrete RGB colormap"""
    with TestingCanvas(size=size, bgcolor='w') as c:
        idata = np.linspace(255, 0, size[0]*size[1]).astype(np.ubyte)
        data = idata.reshape((size[0], size[1]))
        image = Image(cmap=Colormap(colors=['r', 'g', 'b'],
                                    interpolation='zero'),
                      clim='auto', parent=c.scene)
        image.set_data(data)
        assert_image_approved(c.render(), "visuals/colormap_rgb.png")


@requires_application()
def test_colormap_discrete_nu():
    """Test discrete colormap with non-uniformly distributed control-points"""
    with TestingCanvas(size=size, bgcolor='w') as c:
        idata = np.linspace(255, 0, size[0]*size[1]).astype(np.ubyte)
        data = idata.reshape((size[0], size[1]))
        image = Image(cmap=Colormap(np.array([[0, .75, 0], [.75, .25, .5]]),
                                    [0., .25, 1.], interpolation='zero'),
                      clim='auto', parent=c.scene)
        image.set_data(data)
        assert_image_approved(c.render(), "visuals/colormap_nu.png")


@requires_application()
def test_colormap_single_hue():
    """Test colormap support using a single hue()"""
    from vispy.color.colormap import SingleHue
    with TestingCanvas(size=size, bgcolor='w') as c:
        idata = np.linspace(255, 0, size[0]*size[1]).astype(np.ubyte)
        data = idata.reshape((size[0], size[1]))
        cmap = SingleHue(255)
        image = Image(cmap=cmap,
                      clim='auto', parent=c.scene)
        image.set_data(data)
        assert_image_approved(c.render(), "visuals/colormap_hue.png")


@requires_application()
def test_colormap_coolwarm():
    """Test colormap support using coolwarm preset colormap"""
    with TestingCanvas(size=size, bgcolor='w') as c:
        idata = np.linspace(255, 0, size[0]*size[1]).astype(np.ubyte)
        data = idata.reshape((size[0], size[1]))
        image = Image(cmap='coolwarm', clim='auto', parent=c.scene)
        image.set_data(data)
        assert_image_approved(c.render(), "visuals/colormap_coolwarm.png")


@requires_application()
def test_colormap_CubeHelix():
    """Test colormap support using cubehelix colormap in only blues"""
    from vispy.color.colormap import CubeHelixColormap
    with TestingCanvas(size=size, bgcolor='w') as c:
        idata = np.linspace(255, 0, size[0]*size[1]).astype(np.ubyte)
        data = idata.reshape((size[0], size[1]))
        cmap = CubeHelixColormap(rot=0, start=0)
        image = Image(cmap=cmap,
                      clim='auto', parent=c.scene)
        image.set_data(data)
        assert_image_approved(c.render(), "visuals/colormap_cubehelix.png")


run_tests_if_main()
