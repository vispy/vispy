""" Tests to quickly see if the backends look good.
This tests only to see if all the necessary methods are implemented,
whether all the right events are mentioned, and whether the keymap
contains all keys that should be supported.

This test basically checks whether nothing was forgotten, not that the
implementation is corect.

"""

import vispy
from vispy import keys
from vispy.app.backends import requires_pyglet, requires_qt, requires_glfw


class BaseTestmodule:

    def __init__(self, module=None):
        self._module = module

    def test_keymap(self):
        """ Test that the keymap contains all keys supported by vispy.
        """
        keymap = self._module.KEYMAP
        vispy_keys = keymap.values()
        for keyname in dir(keys):
            if keyname.upper() != keyname:
                continue
            key = getattr(keys, keyname)
            assert key in vispy_keys

    def test_methods(self):
        """ Test that all _vispy_x methods are there.
        """
        exceptions = (
            '_vispy_get_native_canvas',
            '_vispy_get_native_timer',
            '_vispy_get_native_app',
            '_vispy_mouse_move',
            '_vispy_mouse_press',
            '_vispy_mouse_release',
            '_vispy_get_geometry')  # defined in base class

        Klass = self._module.CanvasBackend
        KlassRef = vispy.app.canvas.CanvasBackend
        for key in dir(KlassRef):
            if not key.startswith('__'):
                method = getattr(Klass, key)
                if key not in exceptions:
                    if hasattr(method, '__module__'):
                        mod_str = method.__module__  # Py3k
                    else:
                        mod_str = method.im_func.__module__
                    assert mod_str == self._module.__name__, \
                        "Method %s.%s not defined in %s" \
                        % (Klass, key, self._module.__name__)

        Klass = self._module.TimerBackend
        KlassRef = vispy.app.timer.TimerBackend
        for key in dir(KlassRef):
            if not key.startswith('__'):
                method = getattr(Klass, key)
                if key not in exceptions:
                    if hasattr(method, '__module__'):
                        # Py3k
                        assert method.__module__ == self._module.__name__
                    else:
                        t = method.im_func.__module__ == self._module.__name__
                        assert t

        Klass = self._module.ApplicationBackend
        KlassRef = vispy.app.application.ApplicationBackend
        for key in dir(KlassRef):
            if not key.startswith('__'):
                method = getattr(Klass, key)
                if key not in exceptions:
                    if hasattr(method, '__module__'):
                        # Py3k
                        assert method.__module__ == self._module.__name__
                    else:
                        t = method.im_func.__module__ == self._module.__name__
                        assert t

    def test_events(self):
        """ Test that all events seem to be emitted.
        """
        # Get text
        fname = self._module.__file__.strip('c')
        text = open(fname, 'rb').read().decode('utf-8')

        canvas = vispy.app.Canvas(create_native=False)
        # Stylus and touch are ignored because they are not yet implemented.
        # Mouse events are emitted from the CanvasBackend base class.
        ignore = set(['stylus', 'touch', 'mouse_press',
                      'mouse_move', 'mouse_release'])
        eventNames = set(canvas.events._emitters.keys()) - ignore

        for name in eventNames:
            assert 'events.%s' % name in text, ('events.%s does not appear '
                                                'in %s' % (name, fname))


class Test_TemplateBackend(BaseTestmodule):

    def __init__(self):
        from vispy.app.backends import _template
        BaseTestmodule.__init__(self, _template)


class Test_QtBackend(BaseTestmodule):

    @requires_qt()
    def __init__(self):
        from vispy.app.backends import _qt
        BaseTestmodule.__init__(self, _qt)


class Test_PygletBackend(BaseTestmodule):

    @requires_pyglet()
    def __init__(self):
        from vispy.app.backends import _pyglet
        BaseTestmodule.__init__(self, _pyglet)


class Test_GlfwBackend(BaseTestmodule):

    @requires_glfw()
    def __init__(self):
        from vispy.app.backends import _glfw
        BaseTestmodule.__init__(self, _glfw)


class Test_GlutBackend(BaseTestmodule):

    def __init__(self):
        from vispy.app.backends import _glut
        BaseTestmodule.__init__(self, _glut)
