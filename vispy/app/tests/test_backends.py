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
from vispy.testing import requires_application
from vispy.app import default_app
from vispy.app.backends import _template


def _test_module_properties(_module=None):
    """Test application module"""
    if _module is None:
        default_app.use()
        _module = default_app.backend_module

    # Test that the keymap contains all keys supported by vispy.
    keymap = _module.KEYMAP
    vispy_keys = keymap.values()
    for keyname in dir(keys):
        if keyname.upper() != keyname:
            continue
        key = getattr(keys, keyname)
        assert key in vispy_keys
    
    # For Qt backend, we have a common implementation
    alt_modname = ''
    if _module.__name__.split('.')[-1] in ('_pyside', '_pyqt4'):
        alt_modname = _module.__name__.rsplit('.', 1)[0] + '._qt'
    
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
                assert mod_str in (_module.__name__, alt_modname), \
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
                    assert method.__module__ in (_module.__name__, alt_modname)
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
                    assert method.__module__ in (_module.__name__, alt_modname)
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
    
    if not alt_modname:  # Only check for non-proxy modules
        for name in eventNames:
            assert 'events.%s' % name in text, ('events.%s does not appear '
                                                'in %s' % (name, fname))


def test_template():
    """Test application module template"""
    _test_module_properties(_template)
    assert_raises(NotImplementedError, _template._set_config, dict())
    a = _template.ApplicationBackend()
    print(a._vispy_get_backend_name())
    for method in (a._vispy_process_events, a._vispy_run, a._vispy_quit,
                   a._vispy_get_native_app):
        assert_raises(NotImplementedError, method)

    c = _template.CanvasBackend(None)
    print(c._vispy_get_native_canvas())
    for method in (c.events_to_emit, c._vispy_set_current,
                   c._vispy_swap_buffers, c._vispy_update, c._vispy_close,
                   c._vispy_get_size, c._vispy_get_position):
        assert_raises(NotImplementedError, method)
    for method in (c._vispy_set_title, c._vispy_set_visible):
        assert_raises(NotImplementedError, method, 0)
    for method in (c._vispy_set_size, c._vispy_set_position):
        assert_raises(NotImplementedError, method, 0, 0)


@requires_application()
def test_actual():
    """Test actual application module"""
    _test_module_properties(None)
