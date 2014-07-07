import numpy as np
from vispy.util import make_png
from vispy.util.dataio import _check_img_lib, imread
from numpy.testing import assert_array_equal

has_img_lib = not all(c is None for c in _check_img_lib())
requires_img_lib = np.testing.dec.skipif(not has_img_lib, 'imageio or PIL '
                                         'required')


@requires_img_lib
def test_make_png():
    """ Test to ensure that make_png functions correctly.
    Save random RGBA and RGB arrays onto disk as PNGs using make_png.
    Read them back with an image library and check whether the array
    saved is equal to the array read.
    """

    ## RGBA
    # Create random RGBA array as type ubyte
    rgba_save = np.random.randint(256, size=(100, 100, 4)).astype(np.ubyte)
    # Save RGBA with make_png
    with open('rgba.png', 'wb') as f1:
        f1.write(make_png(rgba_save))
    # Read back and check
    rgba_read = imread('rgba.png', 'PNG')
    assert_array_equal(rgba_save, rgba_read)

    ## RGB
    # Get rid of the alpha for RGB
    rgb_save = rgba_save[:, :, :3]
    # Save RGB with make_png
    with open('rgb.png', 'wb') as f2:
        f2.write(make_png(rgb_save))
    # Read back and check
    rgb_read = imread('rgb.png', 'PNG')
    assert_array_equal(rgb_save, rgb_read)
