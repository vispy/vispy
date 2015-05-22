# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import numpy as np
from numpy.testing import assert_array_equal, assert_allclose
from os import path as op
import warnings

from vispy.io import load_crate, imsave, imread, read_png, write_png
from vispy.testing import requires_img_lib, run_tests_if_main
from vispy.util import _TempDir

temp_dir = _TempDir()


def test_make_png():
    """ Test to ensure that make_png functions correctly.
    """
    # Save random RGBA and RGB arrays onto disk as PNGs using make_png.
    # Read them back with an image library and check whether the array
    # saved is equal to the array read.

    # Create random RGBA array as type ubyte
    rgba_save = np.random.randint(256, size=(100, 100, 4)).astype(np.ubyte)
    # Get rid of the alpha for RGB
    rgb_save = rgba_save[:, :, :3]
    # Output file should be in temp
    png_out = op.join(temp_dir, 'random.png')

    # write_png implicitly tests _make_png
    for rgb_a in (rgba_save, rgb_save):
        write_png(png_out, rgb_a)
        rgb_a_read = read_png(png_out)
        assert_array_equal(rgb_a, rgb_a_read)


@requires_img_lib()
def test_read_write_image():
    """Test reading and writing of images"""
    fname = op.join(temp_dir, 'out.png')
    im1 = load_crate()
    imsave(fname, im1, format='png')
    with warnings.catch_warnings(record=True):  # PIL unclosed file
        im2 = imread(fname)
    assert_allclose(im1, im2)


run_tests_if_main()
