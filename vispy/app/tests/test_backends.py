""" Tests to quickly see if the backends look good.
This tests only to see if all the necessary methods are implemented,
whether all the right events are mentioned, and whether the keymap
contains all keys that should be supported.

This test basically checks whether nothing was forgotten, not that the
implementation is corect.

"""

import sys

import vispy
from vispy import keys

class BaseTestmodule:

    def __init__(self, module=None):
        self._module = module
        if module is None:
            print("Skipping %s." % self.__class__.__name__)
            self.test_events = lambda : None
            self.test_keymap = lambda : None
            self.test_methods = lambda : None


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
        exceptions = ('_vispy_get_native_canvas', '_vispy_get_native_timer', '_vispy_get_native_app',
                      '_vispy_mouse_move', '_vispy_mouse_press', '_vispy_mouse_release')

        Klass = self._module.CanvasBackend
        KlassRef = vispy.app.canvas.CanvasBackend
        for key in dir(KlassRef):
            if not key.startswith('__'):
                method = getattr(Klass, key)
                if key not in exceptions:
                    if hasattr(method, '__module__'):
                        mod_str = method.__module__ # Py3k
                    else:
                        mod_str = method.im_func.__module__
                    assert mod_str == self._module.__name__, "Method %s.%s not defined in %s"%(Klass, key, self._module.__name__)

        Klass = self._module.TimerBackend
        KlassRef = vispy.app.timer.TimerBackend
        for key in dir(KlassRef):
            if not key.startswith('__'):
                method = getattr(Klass, key)
                if key not in exceptions:
                    if hasattr(method, '__module__'):
                        assert method.__module__ == self._module.__name__ # Py3k
                    else:
                        assert method.im_func.__module__ == self._module.__name__

        Klass = self._module.ApplicationBackend
        KlassRef = vispy.app.application.ApplicationBackend
        for key in dir(KlassRef):
            if not key.startswith('__'):
                method = getattr(Klass, key)
                if key not in exceptions:
                    if hasattr(method, '__module__'):
                        assert method.__module__ == self._module.__name__ # Py3k
                    else:
                        assert method.im_func.__module__ == self._module.__name__


    def test_events(self):
        """ Test that all events seem to be emitted.
        """
        # Get text
        fname = self._module.__file__.strip('c')
        text = open(fname, 'rb').read().decode('utf-8')

        canvas = vispy.app.Canvas(native=None)
        # Stylus and touch are ignored because they are not yet implemented.
        # Mouse events are emitted from the CanvasBackend base class.
        ignore = set(['stylus', 'touch', 'mouse_press', 'mouse_move', 'mouse_release'])
        eventNames = set(canvas.events._emitters.keys()) - ignore

        for name in eventNames:
            assert 'events.%s'%name in text, 'events.%s does not appear in %s'%(name, fname)



class Test_TemplateBackend(BaseTestmodule):
    def __init__(self):
        from vispy.app.backends import template
        BaseTestmodule.__init__(self, template)

class Test_QtBackend(BaseTestmodule):
    def __init__(self):
        try:
            from vispy.app.backends import qt
        except ImportError:
            BaseTestmodule.__init__(self, None)
        else:
            BaseTestmodule.__init__(self, qt)

class Test_PygletBackend(BaseTestmodule):
    def __init__(self):
        if sys.version_info[0] == 3:
            pyglet = None
        else:
            try:
                from vispy.app.backends import pyglet
            except Exception as err:
                print("Error imporing pyglet:\n%s" % str(err))
                pyglet = None
        BaseTestmodule.__init__(self, pyglet)

class Test_GlutBackend(BaseTestmodule):
    def __init__(self):
        from vispy.app.backends import glut
        BaseTestmodule.__init__(self, glut)



if __name__ == '__main__':

    for klass in [  Test_TemplateBackend,
                    Test_QtBackend,
                    Test_PygletBackend,
                    Test_GlutBackend
                  ]:
        test = klass()
        test.test_keymap()
        test.test_methods()
        test.test_events()
        print('ok %s' % klass.__name__)
