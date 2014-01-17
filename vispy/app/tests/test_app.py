import numpy as np
from nose.tools import assert_equal, assert_true, assert_raises

from vispy.app import Application, Canvas, Timer
from vispy.app.backends import has_qt, has_pyglet

from vispy.gloo.program import Program
from vispy.gloo.shader import VertexShader, FragmentShader, ShaderError


requires_qt = np.testing.dec.skipif(not has_qt(), 'Requires QT')
requires_pyglet = np.testing.dec.skipif(not has_pyglet(), 'Requires QT-UIC')
bad_glut = np.testing.dec.skipif(True, 'GLUT window causes segfaults on 2.7 '
                                 'and fails on 2.6')  # XXX should fix

def on_mouse_move(self, *args):
    return


def _test_application(backend):
    """Test application running"""
    app = Application()
    app.use(backend)
    app.process_events()
    assert_equal(app.backend_name, backend)

    # Canvas
    canvas = Canvas(title='me', app=app, show=True, position=[0, 0, 1, 1])
    assert_true(canvas.app is app)
    assert_true(canvas.native)
    assert_true(canvas.size >= (1, 1))
    canvas.resize(canvas.size[0] - 1, canvas.size[1] - 1)
    assert_true(canvas.position >= (0, 0))
    canvas.move(canvas.position[0] + 1, canvas.position[0] + 1)
    assert_equal(canvas.title, 'me')
    canvas.title = 'you'
    canvas.position = (0, 0)
    canvas.connect(on_mouse_move)
    canvas.show()

    # GLOO: should have an OpenGL context already, so these should work
    vert = VertexShader("void main (void) {gl_Position = pos;}")
    frag = FragmentShader("void main (void) {gl_FragColor = pos;}")
    program = Program(vert, frag)
    assert_raises(ShaderError, program.activate)

    vert = VertexShader("uniform vec4 pos;"
                        "void main (void) {gl_Position = pos;}")
    frag = FragmentShader("uniform vec4 pos;"
                          "void main (void) {gl_FragColor = pos;}")
    program = Program(vert, frag)
    uniform = program.uniforms[0]
    uniform.set_data([1, 2, 3, 4])
    program.activate()  # should print
    uniform.upload(program)

    vert = VertexShader("attribute vec4 pos;"
                        "void main (void) {gl_Position = pos;}")
    frag = FragmentShader("void main (void) {}")
    program = Program(vert, frag)
    attribute = program.attributes[0]
    attribute.set_data([1, 2, 3, 4])
    program.activate()
    attribute.upload(program)

    # Timer
    timer = Timer(interval=0.001, connect=on_mouse_move, iterations=2,
                  start=True, app=app)
    timer.interval = 0.002
    assert_equal(timer.interval, 0.002)
    assert_true(timer.running)
    timer.stop()
    assert_true(not timer.running)
    assert_true(timer.native)
    timer.disconnect()

    # cleanup
    canvas.swap_buffers()
    canvas.update()
    canvas.close()
    app.quit()


@bad_glut
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
