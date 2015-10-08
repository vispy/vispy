import numpy as np
import sys
from collections import namedtuple
from time import sleep

from numpy.testing import assert_array_equal

from vispy.app import use_app, Canvas, Timer, MouseEvent, KeyEvent
from vispy.app.base import BaseApplicationBackend
from vispy.testing import (requires_application, SkipTest, assert_is,
                           assert_in, run_tests_if_main,
                           assert_equal, assert_true, assert_raises)
from vispy.util import keys, use_log_level

from vispy.gloo.program import (Program, VertexBuffer, IndexBuffer)
from vispy.gloo.util import _screenshot
from vispy.gloo import gl
from vispy.ext.six.moves import StringIO

gl.use_gl('gl2 debug')


def on_nonexist(self, *args):
    return


def on_mouse_move(self, *args):
    return


def _on_mouse_move(self, *args):
    return


def _test_callbacks(canvas):
    """Tests input capabilities, triaging based on backend"""
    backend_name = canvas._app.backend_name
    backend = canvas._backend
    if backend_name.lower() == 'pyglet':
        # Test Pyglet callbacks can take reasonable args
        backend.on_resize(100, 100)
        backend.our_draw_func()
        backend.on_mouse_press(10, 10, 1)
        backend.on_mouse_release(10, 11, 1)
        backend.on_mouse_motion(10, 12, 0, 1)
        backend.on_mouse_drag(10, 13, 0, 1, 1, 0)
        backend.on_mouse_scroll(10, 13, 1, 1)
        backend.on_key_press(10, 0)
        backend.on_key_release(10, 0)
        backend.on_text('foo')
    elif backend_name.lower() == 'glfw':
        # Test GLFW callbacks can take reasonable args
        _id = backend._id
        backend._on_draw(_id)
        backend._on_resize(_id, 100, 100)
        
        backend._on_key_press(_id, 340, 340, 1, 0)  # Shift.
        backend._on_key_press(_id, 50, 50, 1, 0)    # 2
        backend._on_key_char(_id, 50)
        backend._on_key_press(_id, 50, 50, 0, 0)
        backend._on_key_press(_id, 340, 340, 0, 0)

        backend._on_key_press(_id, 65, 65, 1, 0)    # Plain A
        backend._on_key_char(_id, 197)              # Unicode A.
        backend._on_key_char(_id, 197)              # Repeat A.
        backend._on_key_press(_id, 65, 65, 0, 0)

        backend._on_mouse_button(_id, 1, 1, 0)
        backend._on_mouse_scroll(_id, 1, 0)
        backend._on_mouse_motion(_id, 10, 10)
        backend._on_close(_id)
    elif any(x in backend_name.lower() for x in ('qt', 'pyside')):
        # constructing fake Qt events is too hard :(
        pass
    elif 'sdl2' in backend_name.lower():
        event = namedtuple('event', ['type', 'window', 'motion', 'button',
                                     'wheel', 'key'])
        event.type = 512  # WINDOWEVENT
        event.window = namedtuple('window', ['event', 'data1', 'data2'])
        event.motion = namedtuple('motion', ['x', 'y'])
        event.button = namedtuple('button', ['x', 'y', 'button'])
        event.wheel = namedtuple('wheel', ['x', 'y'])
        event.key = namedtuple('key', ['keysym'])
        event.key.keysym = namedtuple('keysym', ['mod', 'sym'])

        event.window.event = 5  # WINDOWEVENT_RESIZED
        event.window.data1 = 10
        event.window.data2 = 20
        backend._on_event(event)

        event.type = 1024  # SDL_MOUSEMOTION
        event.motion.x, event.motion.y = 1, 1
        backend._on_event(event)

        event.type = 1025  # MOUSEBUTTONDOWN
        event.button.x, event.button.y, event.button.button = 1, 1, 1
        backend._on_event(event)
        event.type = 1026  # MOUSEBUTTONUP
        backend._on_event(event)

        event.type = 1027  # sdl2.SDL_MOUSEWHEEL
        event.wheel.x, event.wheel.y = 0, 1
        backend._on_event(event)

        event.type = 768  # SDL_KEYDOWN
        event.key.keysym.mod = 1073742049  # SLDK_LSHIFT
        event.key.keysym.sym = 1073741906  # SDLK_UP
        backend._on_event(event)
        event.type = 769  # SDL_KEYUP
        backend._on_event(event)
    elif 'wx' in backend_name.lower():
        # Constructing fake wx events is too hard
        pass
    elif 'osmesa' in backend_name.lower():
        # No events for osmesa backend
        pass
    else:
        raise ValueError


@requires_application()
def test_run():
    """Test app running"""
    for _ in range(2):
        with Canvas(size=(100, 100), show=True, title='run') as c:
            @c.events.draw.connect
            def draw(event):
                print(event)  # test event __repr__
                c.app.quit()
            c.update()
            c.app.run()
        c.app.quit()  # make sure it doesn't break if a user quits twice


@requires_application()
def test_capability():
    """Test application capability enumeration"""
    non_default_vals = dict(title='foo', size=[100, 100], position=[0, 0],
                            show=True, decorate=False, resizable=False,
                            vsync=True)  # context is tested elsewhere
    good_kwargs = dict()
    bad_kwargs = dict()
    with Canvas() as c:
        for key, val in c.app.backend_module.capability.items():
            if key in non_default_vals:
                if val:
                    good_kwargs[key] = non_default_vals[key]
                else:
                    bad_kwargs[key] = non_default_vals[key]
    # ensure all settable values can be set
    with Canvas(**good_kwargs):
        # some of these are hard to test, and the ones that are easy are
        # tested elsewhere, so let's just make sure it runs here
        pass
    # ensure that *any* bad argument gets caught
    for key, val in bad_kwargs.items():
        assert_raises(RuntimeError, Canvas, **{key: val})


@requires_application()
def test_application():
    """Test application running"""
    app = use_app()
    print(app)  # __repr__ without app
    app.create()
    wrong = 'glfw' if app.backend_name.lower() != 'glfw' else 'pyqt4'
    assert_raises(RuntimeError, use_app, wrong)
    app.process_events()
    print(app)  # test __repr__

    assert_raises(ValueError, Canvas, keys='foo')
    assert_raises(TypeError, Canvas, keys=dict(escape=1))
    assert_raises(ValueError, Canvas, keys=dict(escape='foo'))  # not an attr

    pos = [0, 0] if app.backend_module.capability['position'] else None
    size = (100, 100)
    # Use "with" statement so failures don't leave open window
    # (and test context manager behavior)
    title = 'default'
    with Canvas(title=title, size=size, app=app, show=True,
                position=pos) as canvas:
        context = canvas.context
        assert_true(canvas.create_native() is None)  # should be done already
        assert_is(canvas.app, app)
        assert_true(canvas.native)
        assert_equal('swap_buffers', canvas.events.draw.callback_refs[-1])

        canvas.measure_fps(0.001)
        sleep(0.002)
        canvas.update()
        app.process_events()
        assert_true(canvas.fps > 0)

        # Other methods
        print(canvas)  # __repr__
        assert_equal(canvas.title, title)
        canvas.title = 'you'
        with use_log_level('warning', record=True, print_msg=False) as l:
            if app.backend_module.capability['position']:
                # todo: disable more tests based on capability
                canvas.position = pos
            canvas.size = size
        if 'ipynb_vnc' in canvas.app.backend_name.lower():
            assert_true(len(l) >= 1)
        else:
            assert_true(len(l) == 0)
        canvas.connect(on_mouse_move)
        assert_raises(ValueError, canvas.connect, _on_mouse_move)
        if sys.platform != 'darwin':  # XXX knownfail, prob. needs warmup
            canvas.show(False)
            canvas.show()
        app.process_events()
        assert_raises(ValueError, canvas.connect, on_nonexist)
        # deprecation of "paint"
        with use_log_level('info', record=True, print_msg=False) as log:
            olderr = sys.stderr
            try:
                fid = StringIO()
                sys.stderr = fid

                @canvas.events.paint.connect
                def fake(event):
                    pass
            finally:
                sys.stderr = olderr
        assert_equal(len(log), 1)
        assert_in('deprecated', log[0])

        # screenshots
        gl.glViewport(0, 0, *size)
        ss = _screenshot()
        assert_array_equal(ss.shape, size + (4,))
        assert_equal(len(canvas._backend._vispy_get_geometry()), 4)
        if sys.platform != 'win32':  # XXX knownfail for windows
            assert_array_equal(canvas.size, size)
        assert_equal(len(canvas.position), 2)  # XXX knawnfail, doesn't "take"

        # GLOO: should have an OpenGL context already, so these should work
        vert = "void main (void) {gl_Position = pos;}"
        frag = "void main (void) {gl_FragColor = pos;}"
        program = Program(vert, frag)
        assert_raises(RuntimeError, program.glir.flush, context.shared.parser)
        
        vert = "uniform vec4 pos;\nvoid main (void) {gl_Position = pos;}"
        frag = "uniform vec4 pos;\nvoid main (void) {gl_FragColor = pos;}"
        program = Program(vert, frag)
        # uniform = program.uniforms[0]
        program['pos'] = [1, 2, 3, 4]
        
        vert = "attribute vec4 pos;\nvoid main (void) {gl_Position = pos;}"
        frag = "void main (void) {}"
        program = Program(vert, frag)
        # attribute = program.attributes[0]
        program["pos"] = [1, 2, 3, 4]
        
        # use a real program
        program._glir.clear()
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
        program.bind(VertexBuffer(data))
        program['u_model'] = np.eye(4, dtype=np.float32)
        # different codepath if no call to activate()
        program.draw(gl.GL_POINTS)
        subset = IndexBuffer(np.arange(10, dtype=np.uint32))
        program.draw(gl.GL_POINTS, subset)

        # bad programs
        frag_bad = ("varying vec4 v_colors")  # no semicolon
        program = Program(vert, frag_bad)
        assert_raises(RuntimeError, program.glir.flush, context.shared.parser)
        frag_bad = None  # no fragment code. no main is not always enough
        assert_raises(ValueError, Program, vert, frag_bad)

        # Timer
        timer = Timer(interval=0.001, connect=on_mouse_move, iterations=2,
                      start=True, app=app)
        timer.start()
        timer.interval = 0.002
        assert_equal(timer.interval, 0.002)
        assert_true(timer.running)
        sleep(.003)
        assert_true(timer.elapsed >= 0.002)
        timer.stop()
        assert_true(not timer.running)
        assert_true(timer.native)
        timer.disconnect()

        # test that callbacks take reasonable inputs
        _test_callbacks(canvas)

        # cleanup
        canvas.swap_buffers()
        canvas.update()
        app.process_events()
        # put this in even though __exit__ will call it to make sure we don't
        # have problems calling it multiple times
        canvas.close()  # done by context


@requires_application()
def test_fs():
    """Test fullscreen support"""
    a = use_app()
    if not a.backend_module.capability['fullscreen']:
        return
    assert_raises(TypeError, Canvas, fullscreen='foo')
    if (a.backend_name.lower() == 'glfw' or
            (a.backend_name.lower() == 'sdl2' and sys.platform == 'darwin')):
        raise SkipTest('Backend takes over screen')
    with use_log_level('warning', record=True, print_msg=False) as l:
        with Canvas(fullscreen=False) as c:
            assert_equal(c.fullscreen, False)
            c.fullscreen = True
            assert_equal(c.fullscreen, True)
    assert_equal(len(l), 0)
    with use_log_level('warning', record=True, print_msg=False):
        # some backends print a warning b/c fullscreen can't be specified
        with Canvas(fullscreen=0) as c:
            assert_equal(c.fullscreen, True)


@requires_application()
def test_close_keys():
    """Test close keys"""
    c = Canvas(keys='interactive')
    x = list()

    @c.events.close.connect
    def closer(event):
        x.append('done')
    c.events.key_press(key=keys.ESCAPE, text='', modifiers=[])
    assert_equal(len(x), 1)  # ensure the close event was sent
    c.app.process_events()


@requires_application()
def test_event_order():
    """Test event order"""
    x = list()

    class MyCanvas(Canvas):
        def on_initialize(self, event):
            x.append('init')

        def on_draw(self, event):
            sz = True if self.size is not None else False
            x.append('draw size=%s show=%s' % (sz, show))

        def on_close(self, event):
            x.append('close')

    for show in (False, True):
        # clear our storage variable
        while x:
            x.pop()
        with MyCanvas(show=show) as c:
            c.update()
            c.app.process_events()

        print(x)
        assert_true(len(x) >= 3)
        assert_equal(x[0], 'init')
        assert_in('draw size=True', x[1])
        assert_in('draw size=True', x[-2])
        assert_equal(x[-1], 'close')


def test_abstract():
    """Test app abstract template"""
    app = BaseApplicationBackend()
    for fun in (app._vispy_get_backend_name, app._vispy_process_events,
                app._vispy_run, app._vispy_quit):
        assert_raises(NotImplementedError, fun)


def test_mouse_key_events():
    """Test mouse and key events"""
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


run_tests_if_main()
