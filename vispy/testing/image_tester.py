import time
import os
import sys
import inspect
import numpy as np
from .. import scene, config
from ..io import read_png, write_png
from ..gloo.util import _screenshot


global tester
tester = None


def get_tester():
    global tester
    if tester is None:
        tester = ImageTester()
    return tester


def assert_image_approved(image, standard_file, message=None, **kwargs):
    """Check that an image test result matches a pre-approved standard.
    
    If the result does not match, then the user can optionally invoke a GUI
    to compare the images and decide whether to fail the test or save the new
    image as the standard. 
    
    This function will automatically clone the test-data repository into 
    ~/.vispy/test-data. However, it is up to the user to ensure this repository
    is kept up to date and to commit/push new images after they are saved.
    
    Parameters
    ----------
    image : (h, w, 4) ndarray or 'screenshot'
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
    
    if image == "screenshot":
        image = _screenshot(alpha=True)
    if message is None:
        code = inspect.currentframe().f_back.f_code
        message = "%s::%s" % (code.co_filename, code.co_name)
        
    # Make sure we have a test data repo available, possibly invoking git
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


def assert_image_match(im1, im2, min_corr=0.9, px_threshold=50., 
                       px_count=None, max_px_diff=None, avg_px_diff=None, 
                       img_diff=None):
    """Check that two images match.
    
    Images that differ in shape or dtype will fail unconditionally.
    Further tests for similarity depend on the arguments supplied.
    
    Parameters
    ----------
    im1 : (h, w, 4) ndarray
        Test output image
    im2 : (h, w, 4) ndarray
        Test standard image
    min_corr : float or None
        Minimum allowed correlation coefficient between corresponding image
        values (see numpy.corrcoef)
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
    assert im1.dtype == im2.dtype
    if im1.shape != im2.shape:
        # Allow im1 to be an integer multiple larger than im2 to account for
        # High-resolution displays
        ims1 = np.array(im1.shape).astype(float)
        ims2 = np.array(im2.shape).astype(float)
        sr = ims1 / ims2
        assert np.allclose(sr, np.round(sr))
        im1 = resize(im1, im2.shape[:2], 'nearest')
    
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

    if min_corr is not None:
        with np.errstate(invalid='ignore'):
            corr = np.corrcoef(im1.ravel(), im2.ravel())[0, 1]
        assert corr >= min_corr


def _save_failed_test(data, expect, filename):
    from ..io import _make_png
    commit, error = run_subprocess(['git', 'rev-parse',  'HEAD'])
    name = filename.split('/')
    name.insert(-1, commit.strip())
    filename = '/'.join(name)
    host = 'data.vispy.org'

    # concatenate data, expect, and diff into a single image
    ds = data.shape
    es = expect.shape
    
    shape = (max(ds[0], es[0]) + 4, ds[1] + es[1] + 8 + max(ds[1], es[1]), 4)
    img = np.empty(shape, dtype=np.ubyte)
    img[..., :3] = 100
    img[..., 3] = 255
    
    img[2:2+ds[0], 2:2+ds[1], :ds[2]] = data
    img[2:2+es[0], ds[1]+4:ds[1]+4+es[1], :es[2]] = expect
    
    diff = make_diff_image(data, expect)
    img[2:2+diff.shape[0], -diff.shape[1]-2:-2] = diff

    png = _make_png(img)
    conn = httplib.HTTPConnection(host)
    req = urllib.urlencode({'name': filename,
                            'data': base64.b64encode(png)})
    conn.request('POST', '/upload.py', req)
    response = conn.getresponse().read()
    conn.close()
    print("\nImage comparison failed. Test result: %s %s   Expected result: "
          "%s %s" % (data.shape, data.dtype, expect.shape, expect.dtype))
    print("Uploaded to: \nhttp://%s/data/%s" % (host, filename))
    if not response.startswith(b'OK'):
        print("WARNING: Error uploading data to %s" % host)
        print(response)


def make_diff_image(im1, im2):
    """Return image array showing the differences between im1 and im2.
    
    Handles images of different shape. Alpha channels are not compared.
    """
    ds = im1.shape
    es = im2.shape
    
    diff = np.empty((max(ds[0], es[0]), max(ds[1], es[1]), 4), dtype=int)
    diff[..., :3] = 128
    diff[..., 3] = 255
    diff[:ds[0], :ds[1], :min(ds[2], 3)] += im1[..., :3]
    diff[:es[0], :es[1], :min(es[2], 3)] -= im2[..., :3]
    diff = np.clip(diff, 0, 255).astype(np.ubyte)
    return diff


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
        label_text = ['test output', 'standard', 'diff']
        for i, v in enumerate(self.views):
            v.camera = 'panzoom'
            v.camera.aspect = 1
            v.camera.flip = (False, True)
            v.image = scene.Image(parent=v.scene)
            v.label = scene.Text(label_text[i], parent=v, color='yellow', 
                                 anchor_x='left', anchor_y='top')
        
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
