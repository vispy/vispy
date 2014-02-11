import numpy as np
from numpy.testing import assert_array_equal
from nose.tools import assert_equal, assert_true, assert_raises

from vispy.app import (Application, Canvas, Timer, ApplicationBackend,
                       MouseEvent, KeyEvent)
from vispy.app.backends import (requires_pyglet, requires_qt,
                                requires_non_glut)

from vispy.gloo.program import (Program, ProgramError, VertexBuffer,
                                ElementBuffer)
from vispy.gloo.shader import VertexShader, FragmentShader, ShaderError
from vispy.gloo import _screenshot


def on_nonexist(self, *args):
    return


def on_mouse_move(self, *args):
    return


def _on_mouse_move(self, *args):
    return


def _test_application(backend):
    """Test application running"""
    app = Application()
    assert_raises(ValueError, app.use, 'foo')
    app.use(backend)
    wrong = 'Glut' if app.backend_name != 'Glut' else 'Pyglet'
    assert_raises(RuntimeError, app.use, wrong)
    app.process_events()
    if backend is not None:
        # "in" b/c "qt" in "PySide (qt)"
        assert_true(backend in app.backend_name)
    print(app)  # test __repr__

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
    assert_raises(ValueError, canvas.connect, _on_mouse_move)
    canvas.show()
    assert_raises(ValueError, canvas.connect, on_nonexist)

    # screenshots
    ss = _screenshot()
    assert_array_equal(ss.shape[2], 3)  # XXX other dimensions not correct?
    assert_array_equal(canvas._backend._vispy_get_geometry()[2:], canvas.size)

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
    program.detach(vert, frag)
    assert_raises(ShaderError, program.detach, vert)
    assert_raises(ShaderError, program.detach, frag)

    vert = VertexShader("attribute vec4 pos;"
                        "void main (void) {gl_Position = pos;}")
    frag = FragmentShader("void main (void) {}")
    program = Program(vert, frag)
    attribute = program.attributes[0]
    attribute.set_data([1, 2, 3, 4])
    program.activate()
    attribute.upload(program)
    # cannot get element count
    assert_raises(ProgramError, program.draw, 'POINTS')

    # use a real program
    vert = ("uniform mat4 u_model;"
            "attribute vec2 a_position; attribute vec4 a_color;"
            "varying vec4 v_color;"
            "void main (void) {v_color = a_color;"
            "gl_Position = u_model * vec4(a_position, 0.0, 1.0);"
            "v_color = a_color;}")
    frag = "void main() {gl_FragColor = vec4(0, 0, 0, 1);}"
    n, p = 250, 50
    T = np.random.uniform(0, 2 * np.pi, n)
    position = np.zeros((n, 2), dtype=np.float32)
    position[:, 0] = np.cos(T)
    position[:, 1] = np.sin(T)
    color = np.ones((n, 4), dtype=np.float32) * (1, 1, 1, 1)
    data = np.zeros(n * p, [('a_position', np.float32, 2),
                            ('a_color', np.float32, 4)])
    data['a_position'] = np.repeat(position, p, axis=0)
    data['a_color'] = np.repeat(color, p, axis=0)

    program = Program(vert, frag)
    program.set_vars(VertexBuffer(data))
    program['u_model'] = np.eye(4, dtype=np.float32)
    program.draw('POINTS')  # different codepath if no call to activate()
    subset = ElementBuffer(np.arange(10, dtype=np.uint32))
    program.draw('POINTS', subset=subset)

    # bad programs
    frag_bad = ("varying vec4 v_colors")  # no semicolon
    program = Program(vert, frag_bad)
    assert_raises(ShaderError, program.activate)
    frag_bad = None  # no fragment code. no main is not always enough
    program = Program(vert, frag_bad)
    assert_raises(ProgramError, program.activate)

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


# XXX We cannot test GLUT, since there is no safe, cross-platform method for
# closing the main loop!


@requires_non_glut()  # b/c we can't use GLUT, the other option
def test_none():
    """Test default application choosing"""
    _test_application(None)


@requires_pyglet()
def test_pyglet():
    """Test Pyglet application"""
    _test_application('Pyglet')


@requires_qt()
def test_qt():
    """Test Qt application"""
    _test_application('qt')


def test_abstract():
    """Test app abstract template"""
    app = ApplicationBackend()
    for fun in (app._vispy_get_backend_name, app._vispy_process_events,
                app._vispy_run, app._vispy_quit):
        assert_raises(NotImplementedError, fun)


def test_mouse_key_events():
    me = MouseEvent('mouse_press')
    for fun in (me.pos, me.button, me.buttons, me.modifiers, me.delta,
                me.press_event, me.last_event, me.is_dragging):
        fun
    me.drag_events()
    me._forget_last_event()
    me.trail()
    ke = KeyEvent('key_release')
    ke.key
    ke.text
    ke.modifiers
