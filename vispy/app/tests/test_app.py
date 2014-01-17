import numpy as np
from nose.tools import assert_equal

from vispy.app import Application, Canvas
from vispy.app.backends import has_qt, has_pyglet


requires_qt = np.testing.dec.skipif(not has_qt(), 'Requires QT')
requires_pyglet = np.testing.dec.skipif(not has_pyglet(), 'Requires QT-UIC')


def _test_application(backend):
    """Test application running"""
    app = Application()
    app.use(backend)
    assert_equal(app.backend_name, backend)
    canvas = Canvas(app=app)
    canvas.show()
    canvas.close()


@np.testing.dec.skipif(True, 'GLUT window causes segfaults on 2.7 and '
                       'fails on 2.6')
def test_glut():
    """Test GLUT application"""
    _test_application('Glut')


@requires_pyglet
def test_pyglet():
    """Test Pyglet application"""
    _test_application('Pyglet')


@requires_qt
def test_qt():
    """Test Qt application"""
    _test_application('qt')
