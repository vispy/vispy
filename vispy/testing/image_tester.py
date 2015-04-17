import time
import os
import sys
import numpy as np
from .. import scene, config
from ..io import read_png, write_png
from ._testing import _save_failed_test, make_diff_image


global tester
tester = None


def get_tester():
    global tester
    if tester is None:
        tester = ImageTester()
    return tester


def assert_image_approved(image, standard_file, message, **kwargs):
    """Check that an image test result matches a pre-approved standard.
    
    If the result does not match, then the user can optionally invoke a GUI
    to compare the images and decide whether to fail the test or save the new
    image as the standard. 
    
    This function will automatically clone the test-data repository into 
    ~/.vispy/test-data. However, it is up to the user to ensure this repository
    is kept up to date and to commit/push new images after they are saved.
    
    Parameters
    ----------
    image : (h, w, 4) ndarray
        The test result to check
    standard_file : str
        The name of the approved test image to check against. This file name
        is relative to the root of the vispy test-data repository and will
        be automatically fetched.
    message : str
        A string description of the image. It is recommended to describe 
        specific features that an auditor should look for when deciding whether
        to fail a test.
        
    Extra keyword arguments are used to set the thresholds for automatic image
    comparison (see ``assert_image_match()``).    
    """
    
    # First make sure we have a test data repo available, possibly invoking 
    # git
    data_path = config['test_data_path']
    git_path = 'https://github.com/vispy/test-data'
    if not os.path.isdir(data_path):
        cmd = 'git clone --depth=3 %s %s' % (git_path, data_path)
        print("Attempting to create git clone of test data repo in %s.." %
              data_path)
        print(cmd)
        rval = os.system(cmd)
        if rval != 0:
            raise RuntimeError("Test data path '%s' does not exist and could "
                               "not be created with git. Either create a git "
                               "clone of %s or set the test_data_path "
                               "variable to an existing clone." % 
                               (data_path, git_path))
    
    # Read the standard image if it exists
    std_file = os.path.join(data_path, standard_file)
    if not os.path.isfile(std_file):
        std_image = None
    else:
        std_image = read_png(std_file)
        
    # If the test image does not match, then we go to audit if requested.
    try:
        assert_image_match(image, std_image, **kwargs)
    except Exception:
        if config['audit_tests']:
            sys.excepthook(*sys.exc_info())
            get_tester().test(image, std_image, message)
            std_path = os.path.dirname(std_file)
            print('Saving new standard image to "%s"' % std_file)
            if not os.path.isdir(std_path):
                os.makedirs(std_path)
            write_png(std_file, image)
        else:
            if std_image is None:
                raise Exception("Test standard %s does not exist." % std_file)
            else:
                if os.getenv('TRAVIS') is not None:
                    _save_failed_test(image, std_image, standard_file)
                raise


def assert_image_match(im1, im2, px_threshold=50., px_count=None, 
                       max_px_diff=None, avg_px_diff=None, img_diff=None):
    """Check that two images match.
    
    Images that differ in shape or dtype will fail unconditionally.
    Further tests for similarity depend on the arguments supplied.
    
    Parameters
    ----------
    im1 : (h, w, 4) ndarray
        Test output image
    im2 : (h, w, 4) ndarray
        Test standard image
    px_threshold : float
        Minimum value difference at which two pixels are considered different
    px_count : int or None
        Maximum number of pixels that may differ
    max_px_diff : float or None
        Maximum allowed difference between pixels
    avg_px_diff : float or None
        Average allowed difference between pixels
    img_diff : float or None
        Maximum allowed summed difference between images 
    """
    assert im1.ndim == 3
    assert im1.shape[2] == 4
    assert im1.shape == im2.shape
    assert im1.dtype == im2.dtype
    
    diff = im1.astype(float) - im2.astype(float)
    if img_diff is not None:
        assert np.abs(diff).sum() <= img_diff
        
    pxdiff = diff.max(axis=2)  # largest value difference per pixel
    mask = np.abs(pxdiff) >= px_threshold
    if px_count is not None:
        assert mask.sum() <= px_count
        
    masked_diff = diff[mask]
    if max_px_diff is not None:
        assert masked_diff.max() <= max_px_diff
    if avg_px_diff is not None:
        assert masked_diff.mean() <= avg_px_diff


class ImageTester(scene.SceneCanvas):
    """Graphical interface for auditing image comparison tests.
    """
    def __init__(self):
        scene.SceneCanvas.__init__(self, size=(1000, 800))
        self.bgcolor = (0.1, 0.1, 0.1, 1)
        self.grid = self.central_widget.add_grid()
        border = (0.3, 0.3, 0.3, 1)
        self.views = (self.grid.add_view(row=0, col=0, border_color=border), 
                      self.grid.add_view(row=0, col=1, border_color=border),
                      self.grid.add_view(row=0, col=2, border_color=border))
        for v in self.views:
            v.camera = 'panzoom'
            v.camera.aspect = 1
            v.camera.flip = (False, True)
            v.image = scene.Image(parent=v.scene)
        
        self.views[1].camera.link(self.views[0].camera)
        self.views[2].camera.link(self.views[0].camera)
        self.console = scene.Console(text_color='white', border_color=border)
        self.grid.add_widget(self.console, row=1, col=0, col_span=3)
        
    def test(self, im1, im2, message):
        self.show()
        self.console.write('------------------')
        self.console.write(message)
        if im2 is None:
            self.console.write('Image1: %s %s   Image2: [no standard]' % 
                               (im1.shape, im1.dtype))
            im2 = np.zeros((1, 1, 3), dtype=np.ubyte)
        else:
            self.console.write('Image1: %s %s   Image2: %s %s' % 
                               (im1.shape, im1.dtype, im2.shape, im2.dtype))
        self.console.write('(P)ass or (F)ail this test?')
        self.views[0].image.set_data(im1)
        self.views[1].image.set_data(im2)
        diff = make_diff_image(im1, im2)

        self.views[2].image.set_data(diff)
        self.views[0].camera.set_range()
        
        self.last_key = None
        while True:
            self.app.process_events()
            if self.last_key is None:
                pass
            elif self.last_key.lower() == 'p':
                self.console.write('PASS')
                break
            elif self.last_key.lower() in ('f', 'esc'):
                self.console.write('FAIL')
                raise Exception("User rejected test result.")
            time.sleep(0.03)
        
        for v in self.views:
            v.image.set_data(np.zeros((1, 1, 3), dtype=np.ubyte))

    def on_key_press(self, event):
        self.last_key = event.key.name
