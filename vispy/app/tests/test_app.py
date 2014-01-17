import numpy as np

from vispy.app import Application, Canvas
from vispy.app.backends import has_qt, has_pyglet


requires_qt = np.testing.dec.skipif(not has_qt(), 'Requires QT')
requires_pyglet = np.testing.dec.skipif(not has_pyglet(), 'Requires QT-UIC')


def _test_application(backend):
    """Test application running"""
    app = Application()
    app.use(backend)
    canvas = Canvas('test', app, True)
    canvas.show()
    canvas.close()
    app.quit()


def test_glut():
    """Test GLUT application"""
    _test_application('glut')


@requires_pyglet
def test_pyglet():
    """Test Pyglet application"""
    _test_application('pyglet')


@requires_qt
def test_qt():
    """Test Qt application"""
    _test_application('qt')
