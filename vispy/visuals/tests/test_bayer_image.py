# -*- coding: utf-8 -*-
import numpy as np

from vispy.scene.visuals import Image, BayerImage
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_match

import imageio


@requires_application()
def test_image():
    """Test image visual"""
    astronaut = imageio.imread('imageio:astronaut.png')
    size = (512, 512)
    with TestingCanvas(size=size, bgcolor='w') as c:
        image = Image(parent=c.scene)
        image.set_data(astronaut)

        expected_render = c.render()
    for bayer_pattern in ['rggb', 'bggr', 'gbrg', 'grbg']:
        do_test_image(bayer_pattern,
                      size=size, image=astronaut, expected_render=expected_render)


def do_test_image(bayer_pattern, size, image, expected_render):
    image_bayer = np.zeros(image.shape[:2], dtype=image.dtype)
    if bayer_pattern == 'bggr':
        image_bayer[0::2, 0::2] = image[0::2, 0::2, 2]
        image_bayer[0::2, 1::2] = image[0::2, 1::2, 1]
        image_bayer[1::2, 0::2] = image[1::2, 0::2, 1]
        image_bayer[1::2, 1::2] = image[1::2, 1::2, 0]
    elif bayer_pattern == 'rggb':
        image_bayer[0::2, 0::2] = image[0::2, 0::2, 0]
        image_bayer[0::2, 1::2] = image[0::2, 1::2, 1]
        image_bayer[1::2, 0::2] = image[1::2, 0::2, 1]
        image_bayer[1::2, 1::2] = image[1::2, 1::2, 2]
    elif bayer_pattern == 'grbg':
        image_bayer[0::2, 0::2] = image[0::2, 0::2, 1]
        image_bayer[0::2, 1::2] = image[0::2, 1::2, 2]
        image_bayer[1::2, 0::2] = image[1::2, 0::2, 0]
        image_bayer[1::2, 1::2] = image[1::2, 1::2, 1]
    elif bayer_pattern == 'gbrg':
        image_bayer[0::2, 0::2] = image[0::2, 0::2, 1]
        image_bayer[0::2, 1::2] = image[0::2, 1::2, 0]
        image_bayer[1::2, 0::2] = image[1::2, 0::2, 2]
        image_bayer[1::2, 1::2] = image[1::2, 1::2, 1]
    else:
        raise ValueError("Typo in test suite")

    with TestingCanvas(size=size, bgcolor='w') as c:
        image = BayerImage(bayer_pattern=bayer_pattern, parent=c.scene)
        image.set_data(image_bayer)
        render_obtained = c.render()

    # alpha channel should be exactly equal
    assert_image_match(render_obtained, expected_render)


run_tests_if_main()
