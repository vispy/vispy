""" Tests to quickly see if the backends look good.
This tests only to see if all the necessary methods are implemented,
whether all the right events are mentioned, and whether the keymap
contains all keys that should be supported.

This test basically checks whether nothing was forgotten, not that the
implementation is corect.

"""

from nose.tools import assert_raises
from inspect import getargspec

import vispy
from vispy import keys
from vispy.app import Application
from vispy.util.testing import requires_application
from vispy.app.backends import _template


@requires_application()
def test_module(_module=None):
    """Test application module"""
    if _module is None:
        a = Application()
        a.use()
        _module = a.backend_module

    # Test that the keymap contains all keys supported by vispy.
    keymap = _module.KEYMAP
    vispy_keys = keymap.values()
    for keyname in dir(keys):
        if keyname.upper() != keyname:
            continue
        key = getattr(keys, keyname)
        assert key in vispy_keys

    # Test that all _vispy_x methods are there.
    exceptions = (
        '_vispy_get_native_canvas',
        '_vispy_get_native_timer',
        '_vispy_get_native_app',
        '_vispy_mouse_move',
        '_vispy_mouse_press',
        '_vispy_mouse_release',
        '_vispy_get_geometry',
        '_process_backend_kwargs')  # defined in base class

    Klass = _module.CanvasBackend
    KlassRef = vispy.app.base.BaseCanvasBackend
    base = KlassRef(None, None)
    for key in dir(KlassRef):
        if not key.startswith('__'):
            method = getattr(Klass, key)
            if key not in exceptions:
                print(key)
                args = [None] * (len(getargspec(method).args) - 1)
                assert_raises(NotImplementedError, getattr(base, key),
                              *args)
                if hasattr(method, '__module__'):
                    mod_str = method.__module__  # Py3k
                else:
                    mod_str = method.im_func.__module__
                assert mod_str == _module.__name__, \
                    "Method %s.%s not defined in %s" \
                    % (Klass, key, _module.__name__)

    Klass = _module.TimerBackend
    KlassRef = vispy.app.timer.TimerBackend
    for key in dir(KlassRef):
        if not key.startswith('__'):
            method = getattr(Klass, key)
            if key not in exceptions:
                if hasattr(method, '__module__'):
                    # Py3k
                    assert method.__module__ == _module.__name__
                else:
                    t = method.im_func.__module__ == _module.__name__
                    assert t

    Klass = _module.ApplicationBackend
    KlassRef = vispy.app.application.ApplicationBackend
    for key in dir(KlassRef):
        if not key.startswith('__'):
            method = getattr(Klass, key)
            if key not in exceptions:
                if hasattr(method, '__module__'):
                    # Py3k
                    assert method.__module__ == _module.__name__
                else:
                    t = method.im_func.__module__ == _module.__name__
                    assert t

    # Test that all events seem to be emitted.
    # Get text
    fname = _module.__file__.strip('c')
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


def test_template():
    """Test backend template"""
    test_module(_template)
