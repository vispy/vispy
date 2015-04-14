import time
import os
import sys
import numpy as np
from .. import scene, config
from ..io import read_png, write_png
from ._testing import _save_failed_test


global tester
tester = None


def get_tester():
    global tester
    if tester is None:
        tester = ImageTester()
    return tester


def assert_image_approved(image, standard_file, message):
    
    # First make sure we have a test data repo available, possibly invoking 
    # git
    data_path = config['test_data_path']
    if not os.path.isdir(data_path):
        git_path = 'https://github.com/vispy/test-data'
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
        assert std_image.shape == image.shape
        assert std_image.dtype == image.dtype
        assert np.all(std_image == image)
    except Exception:
        if config['audit_tests']:
            sys.excepthook(*sys.exc_info())
            get_tester().test(image, std_image, message)
            std_path = os.path.dirname(std_file)
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
        diff = (im1[:im2.shape[0], :im2.shape[1], :3] - 
                im2[:im1.shape[0], :im1.shape[1], :3])

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
