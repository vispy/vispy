"""Tests to quickly see if the backends look good.
This tests only to see if all the necessary methods are implemented,
whether all the right events are mentioned, and whether the keymap
contains all keys that should be supported.

This test basically checks whether nothing was forgotten, not that the
implementation is corect.

"""

import vispy
from vispy import keys
from vispy.testing import (requires_application, assert_in, run_tests_if_main,
                           assert_raises)
from vispy.app import use_app, Application
from vispy.app.backends import _template
from vispy.util import _get_args


class DummyApplication(Application):
    def _use(self, backend_namd):
        pass


def _test_module_properties(_module=None):
    """Test application module"""
    if _module is None:
        app = use_app()
        _module = app.backend_module

    # Test that the keymap contains all keys supported by vispy.
    module_fname = _module.__name__.split('.')[-1]
    if module_fname not in ('_egl', '_osmesa'):  # skip keys for EGL, osmesa
        keymap = _module.KEYMAP
        vispy_keys = keymap.values()
        for keyname in dir(keys):
            if keyname.upper() != keyname:
                continue
            key = getattr(keys, keyname)
            assert_in(key, vispy_keys)

    # For Qt backend, we have a common implementation
    alt_modname = ''
    if module_fname in ('_pyside', '_pyqt4', '_pyqt5', '_pyqt6', '_pyside2', '_pyside6'):
        alt_modname = _module.__name__.rsplit('.', 1)[0] + '._qt'

    # Test that all _vispy_x methods are there.
    exceptions = (
        '_vispy_get_native_canvas',
        '_vispy_get_native_timer',
        '_vispy_get_native_app',
        '_vispy_reuse',
        '_vispy_mouse_move',
        '_vispy_mouse_press',
        '_vispy_mouse_release',
        '_vispy_mouse_double_click',
        '_vispy_detect_double_click',
        '_vispy_get_fb_bind_location',
        '_vispy_get_geometry',
        '_vispy_get_physical_size',
        '_vispy_sleep',
        '_process_backend_kwargs')  # defined in base class

    class KlassRef(vispy.app.base.BaseCanvasBackend):
        def __init__(self, *args, **kwargs):
            pass  # Do not call the base class, since it will check for Canvas
    Klass = _module.CanvasBackend
    base = KlassRef()
    for key in dir(KlassRef):
        if not key.startswith('__'):
            method = getattr(Klass, key)
            if key not in exceptions:
                print(key)
                args = [None] * (len(_get_args(method)) - 1)
                assert_raises(NotImplementedError, getattr(base, key), *args)
                if hasattr(method, '__module__'):
                    mod_str = method.__module__  # Py3k
                else:
                    mod_str = method.im_func.__module__
                assert_in(mod_str, (_module.__name__, alt_modname),
                          "Method %s.%s not defined in %s"
                          % (Klass, key, _module.__name__))

    Klass = _module.TimerBackend
    KlassRef = vispy.app.timer.TimerBackend
    for key in dir(KlassRef):
        if not key.startswith('__'):
            method = getattr(Klass, key)
            if key not in exceptions:
                if hasattr(method, '__module__'):
                    # Py3k
                    assert_in(method.__module__,
                              (_module.__name__, alt_modname))
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
                    assert_in(method.__module__,
                              (_module.__name__, alt_modname))
                else:
                    t = method.im_func.__module__ == _module.__name__
                    assert t

    # Test that all events seem to be emitted.
    # Get text
    fname = _module.__file__.rstrip('c')  # "strip" will break windows!
    with open(fname, 'rb') as fid:
        text = fid.read().decode('utf-8')

    canvas = vispy.app.Canvas(create_native=False, app=DummyApplication())
    # Stylus and touch are ignored because they are not yet implemented.
    # Mouse events are emitted from the CanvasBackend base class.
    ignore = set(['stylus', 'touch', 'mouse_press', 'paint',
                  'mouse_move', 'mouse_release', 'mouse_double_click',
                  'detect_double_click', 'close'])
    if module_fname in ('_egl', '_osmesa'):
        ignore = ignore.union(['mouse_wheel', 'key_release', 'key_press'])
    eventNames = set(canvas.events._emitters.keys()) - ignore

    if not alt_modname:  # Only check for non-proxy modules
        for name in eventNames:
            assert_in('events.%s' % name, text,
                      'events.%s does not appear in %s' % (name, fname))


def test_template():
    """Test application module template"""
    _test_module_properties(_template)
    assert_raises(NotImplementedError, _template._set_config, dict())
    a = _template.ApplicationBackend()
    print(a._vispy_get_backend_name())
    for method in (a._vispy_process_events, a._vispy_run, a._vispy_quit,
                   a._vispy_get_native_app):
        assert_raises(NotImplementedError, method)

    class TemplateCanvasBackend(_template.CanvasBackend):
        def __init__(self, *args, **kwargs):
            pass  # Do not call the base class, since it will check for Canvas
    c = TemplateCanvasBackend()  # _template.CanvasBackend(None)
    print(c._vispy_get_native_canvas())
    for method in (c._vispy_set_current, c._vispy_swap_buffers, c._vispy_close,
                   c._vispy_update, c._vispy_get_size, c._vispy_get_position):
        assert_raises(NotImplementedError, method)
    for method in (c._vispy_set_title, c._vispy_set_visible):
        assert_raises(NotImplementedError, method, 0)
    for method in (c._vispy_set_size, c._vispy_set_position):
        assert_raises(NotImplementedError, method, 0, 0)


@requires_application()
def test_actual():
    """Test actual application module"""
    _test_module_properties(None)


run_tests_if_main()
