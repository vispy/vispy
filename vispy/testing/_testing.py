# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from __future__ import print_function

import numpy as np
import sys
import os
import inspect
import gc
import pytest
import functools

from packaging.version import Version

from ..util.check_environment import has_backend

skipif = pytest.mark.skipif

IS_TRAVIS_CI = "true" in os.getenv("TRAVIS", "")
IS_GITHUB_ACTIONS = "true" in os.getenv("GITHUB_ACTIONS", "")
IS_CI = IS_TRAVIS_CI or IS_GITHUB_ACTIONS


def SkipTest(*args, **kwargs):
    """Backport for raising SkipTest that gives a better traceback."""
    __tracebackhide__ = True
    import pytest
    return pytest.skip(*args, **kwargs)


def _safe_rep(obj, short=False):
    """Helper for assert_* ports"""
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if not short or len(result) < 80:
        return result
    return result[:80] + ' [truncated]...'


def _safe_str(obj):
    """Helper for assert_* ports"""
    try:
        return str(obj)
    except Exception:
        return object.__str__(obj)


def _format_msg(msg, std_msg):
    """Helper for assert_* ports"""
    if msg is None:
        msg = std_msg
    else:
        try:
            msg = '%s : %s' % (std_msg, msg)
        except UnicodeDecodeError:
            msg = '%s : %s' % (_safe_str(std_msg), _safe_str(msg))
    return msg


def nottest(func):
    """Decorator to mark a function or method as *not* a test"""
    func.__test__ = False
    return func


def assert_raises(exp, func, *args, **kwargs):
    """Backport"""
    try:
        func(*args, **kwargs)
    except exp:
        return
    std_msg = '%s not raised' % (_safe_rep(exp))
    raise AssertionError(_format_msg(None, std_msg))


def assert_in(member, container, msg=None):
    """Backport"""
    if member in container:
        return
    std_msg = '%s not found in %s' % (_safe_rep(member), _safe_rep(container))
    raise AssertionError(_format_msg(msg, std_msg))


def assert_true(x, msg=None):
    """Backport"""
    if x:
        return
    std_msg = '%s is not True' % (_safe_rep(x),)
    raise AssertionError(_format_msg(msg, std_msg))


def assert_equal(x, y, msg=None):
    """Backport"""
    if x == y:
        return
    std_msg = '%s not equal to %s' % (_safe_rep(x), _safe_rep(y))
    raise AssertionError(_format_msg(msg, std_msg))


def assert_not_equal(x, y, msg=None):
    """Backport"""
    if x != y:
        return
    std_msg = '%s equal to %s' % (_safe_rep(x), _safe_rep(y))
    raise AssertionError(_format_msg(msg, std_msg))


def assert_not_in(member, container, msg=None):
    """Backport"""
    if member not in container:
        return
    std_msg = '%s found in %s' % (_safe_rep(member), _safe_rep(container))
    raise AssertionError(_format_msg(msg, std_msg))


def assert_is(expr1, expr2, msg=None):
    """Backport"""
    if expr1 is not expr2:
        std_msg = '%s is not %s' % (_safe_rep(expr1), _safe_rep(expr2))
        raise AssertionError(_format_msg(msg, std_msg))


class raises(object):
    """Helper class to test exception raising"""

    def __init__(self, exc):
        self.exc = exc

    def __enter__(self):
        return self

    def __exit__(self, exc_typ, exc, tb):
        if isinstance(exc, self.exc):
            return True
        elif exc is None:
            raise AssertionError("Expected %s (no exception raised)" %
                                 self.exc.__name__)
        else:
            raise AssertionError("Expected %s, got %s instead (%s)" %
                                 (self.exc.__name__, type(exc).__name__, exc))


###############################################################################
# GL stuff

def has_pyopengl():
    try:
        from OpenGL import GL  # noqa, analysis:ignore
    except ImportError:
        return False
    else:
        return True


def requires_pyopengl():
    skip = not has_pyopengl()
    return skipif(skip, reason='Requires PyOpenGL')


def requires_ssl():
    bad = os.getenv('CIBW_BUILDING', 'false') == 'true'
    return skipif(bad, reason='Requires proper SSL support')


###############################################################################
# App stuff


def has_application(backend=None, has=(), capable=()):
    """Determine if a suitable app backend exists"""
    from ..app.backends import BACKEND_NAMES
    # avoid importing other backends if we don't need to
    if backend is None:
        for backend in BACKEND_NAMES:
            if has_backend(backend, has=has, capable=capable):
                good = True
                msg = backend
                break
        else:
            good = False
            msg = 'Requires application backend'
    else:
        good, why = has_backend(backend, has=has, capable=capable,
                                out=['why_not'])
        if not good:
            msg = 'Requires %s: %s' % (backend, why)
        else:
            msg = backend
    return good, msg


def composed(*decs):
    def deco(f):
        for dec in reversed(decs):
            f = dec(f)
        return f
    return deco


def garbage_collect(f):
    # Pytest expects things like the name of the functions not to change
    # Therefore, we must use the functools.wraps decorator on our deco
    @functools.wraps(f)
    def deco(*args, **kwargs):
        gc.collect()
        try:
            return f(*args, **kwargs)
        finally:
            gc.collect()
    return deco


def requires_application(backend=None, has=(), capable=(), force_gc=True):
    """Return a decorator for tests that require an application"""
    good, msg = has_application(backend, has, capable)
    dec_backend = skipif(not good, reason="Skipping test: %s" % msg)
    try:
        import pytest
    except Exception:
        return dec_backend
    dec_app = pytest.mark.vispy_app_test
    funcs = [dec_app, dec_backend]
    if force_gc:
        funcs.append(garbage_collect)
    return composed(*funcs)


def requires_img_lib():
    """Decorator for tests that require an image library"""
    from ..io import _check_img_lib
    if sys.platform.startswith('win'):
        has_img_lib = False  # PIL breaks tests on windows (!)
    else:
        has_img_lib = not all(c is None for c in _check_img_lib())
    return skipif(not has_img_lib, reason='imageio or PIL required')


def has_ipython(version='3.0'):
    """Function that checks the presence of IPython"""
    # typecast version to a string, in case an integer is given
    version = str(version)

    try:
        import IPython  # noqa
    except Exception:
        return False, "IPython library not found"
    else:
        if Version(IPython.__version__) >= Version(version):
            return True, "IPython present"
        else:
            message = (
                "current IPython version: (%s) is "
                "older than expected version: (%s)") % \
                (IPython.__version__, version)

            return False, message


def requires_ipython(version='3.0'):
    ipython_present, message = has_ipython(version)
    return skipif(not ipython_present, reason=message)


def requires_numpydoc():
    try:
        import numpydoc  # noqa
    except Exception:
        present = False
    else:
        present = True
    return skipif(not present, reason='numpydoc is required')


###############################################################################
# Visuals stuff

def _has_scipy(min_version):
    try:
        assert isinstance(min_version, str)
        import scipy  # noqa, analysis:ignore
        this_version = Version(scipy.__version__)
        if this_version < min_version:
            return False
    except Exception:
        return False
    else:
        return True


def requires_scipy(min_version='0.13'):
    return skipif(not _has_scipy(min_version),
                  reason='Requires Scipy version >= %s' % min_version)


def _bad_glfw_decorate(app):
    return app.backend_name == 'Glfw' and \
        app.backend_module.glfw.__version__ == (3, 3, 1)


@nottest
def TestingCanvas(bgcolor='black', size=(100, 100), dpi=None, decorate=None,
                  **kwargs):
    """Avoid importing scene until necessary."""
    # On Windows decorations can force windows to be an incorrect size
    # (e.g., instead of 100x100 they will be 100x248), having no
    # decorations works around this
    from ..scene import SceneCanvas

    class TestingCanvas(SceneCanvas):
        def __init__(self, bgcolor, size, dpi, decorate, **kwargs):
            self._entered = False
            self._wanted_vp = None
            if decorate is None:
                # deal with GLFW's problems
                from vispy.app import use_app
                app = use_app()
                if _bad_glfw_decorate(app):
                    decorate = True
                else:
                    decorate = False
            SceneCanvas.__init__(self, bgcolor=bgcolor, size=size,
                                 dpi=dpi, decorate=decorate,
                                 **kwargs)

        def __enter__(self):
            SceneCanvas.__enter__(self)
            # sometimes our window can be larger than our requsted draw
            # area (e.g. on Windows), and this messes up our tests that
            # typically use very small windows. Here we "fix" it.
            scale = np.array(self.physical_size) / np.array(self.size, float)
            scale = int(np.round(np.mean(scale)))
            self._wanted_vp = 0, 0, size[0] * scale, size[1] * scale
            self.context.set_state(clear_color=self._bgcolor)
            self.context.set_viewport(*self._wanted_vp)
            self._entered = True
            return self

        def draw_visual(self, visual, event=None):
            if not self._entered:
                return
            SceneCanvas.draw_visual(self, visual, event)
            self.context.finish()

    return TestingCanvas(bgcolor, size, dpi, decorate, **kwargs)


@nottest
def save_testing_image(image, location):
    from ..gloo.util import _screenshot
    from ..util import make_png
    if image == "screenshot":
        image = _screenshot(alpha=False)
    with open(location + '.png', 'wb') as fid:
        fid.write(make_png(image))


@nottest
def run_tests_if_main():
    """Run tests in a given file if it is run as a script"""
    local_vars = inspect.currentframe().f_back.f_locals
    if not local_vars.get('__name__', '') == '__main__':
        return
    # we are in a "__main__"
    fname = local_vars['__file__']
    # Run ourselves. post-mortem debugging!
    try:
        import faulthandler
        faulthandler.enable()
    except Exception:
        pass
    import __main__
    try:
        import pytest
        pytest.main(['-s', '--tb=short', fname])
    except ImportError:
        print('==== Running tests in script\n==== %s' % fname)
        run_tests_in_object(__main__)
        print('==== Tests pass')


def run_tests_in_object(ob):
    # Setup
    for name in dir(ob):
        if name.lower().startswith('setup'):
            print('Calling %s' % name)
            getattr(ob, name)()
    # Exec
    for name in sorted(dir(ob), key=lambda x: x.lower()):  # consistent order
        val = getattr(ob, name)
        if name.startswith('_'):
            continue
        elif callable(val) and (name[:4] == 'test' or name[-4:] == 'test'):
            print('Running test-func %s ... ' % name, end='')
            try:
                val()
                print('ok')
            except Exception as err:
                if 'skiptest' in err.__class__.__name__.lower():
                    print('skip')
                else:
                    raise
        elif isinstance(val, type) and 'Test' in name:
            print('== Running test-class %s' % name)
            run_tests_in_object(val())
            print('== Done with test-class %s' % name)
    # Teardown
    for name in dir(ob):
        if name.lower().startswith('teardown'):
            print('Calling %s' % name)
            getattr(ob, name)()
