import numpy as np
from numpy.testing import assert_array_equal
from os import path as op

from vispy.util import make_png, _TempDir
from vispy.util.dataio import imread
from vispy.testing import requires_img_lib

temp_dir = _TempDir()


@requires_img_lib()
def test_make_png():
    """ Test to ensure that make_png functions correctly.
    Save random RGBA and RGB arrays onto disk as PNGs using make_png.
    Read them back with an image library and check whether the array
    saved is equal to the array read.
    """

    # Create random RGBA array as type ubyte
    rgba_save = np.random.randint(256, size=(100, 100, 4)).astype(np.ubyte)
    # Get rid of the alpha for RGB
    rgb_save = rgba_save[:, :, :3]
    # Output file should be in temp
    png_out = op.join(temp_dir, 'random.png')

    for rgb_a in (rgba_save, rgb_save):
        with open(png_out, 'wb') as f:
            f.write(make_png(rgb_a))  # Save array with make_png

        # Read back with a library and check equality
        rgb_a_read = imread(png_out, 'PNG')
        assert_array_equal(rgb_a, rgb_a_read)
