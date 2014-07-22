# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from __future__ import print_function

import numpy as np
import os
from ..app import Canvas

###############################################################################
# Adapted from Python's unittest2 (which is wrapped by nose)
# http://docs.python.org/2/license.html

try:
    from unittest.case import SkipTest
except ImportError:
    try:
        from unittest2.case import SkipTest
    except ImportError:
        class SkipTest(Exception):
            pass


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


def assert_in(member, container, msg=None):
    """Backport for old nose.tools"""
    if member in container:
        return
    std_msg = '%s not found in %s' % (_safe_rep(member), _safe_rep(container))
    msg = _format_msg(msg, std_msg)
    raise AssertionError(msg)


def assert_not_in(member, container, msg=None):
    """Backport for old nose.tools"""
    if member not in container:
        return
    std_msg = '%s found in %s' % (_safe_rep(member), _safe_rep(container))
    msg = _format_msg(msg, std_msg)
    raise AssertionError(msg)


def assert_is(expr1, expr2, msg=None):
    """Backport for old nose.tools"""
    if expr1 is not expr2:
        std_msg = '%s is not %s' % (_safe_rep(expr1), _safe_rep(expr2))
        raise AssertionError(_format_msg(msg, std_msg))


###############################################################################
# GL stuff

def _has_pyopengl():
    try:
        from OpenGL import GL  # noqa, analysis:ignore
    except Exception:
        return False
    else:
        return True


def requires_pyopengl():
    return np.testing.dec.skipif(not _has_pyopengl(), 'Requires PyOpenGL')


###############################################################################
# App stuff

def has_backend(backend, has=(), capable=(), out=()):
    from ..app.backends import BACKENDMAP
    using = os.getenv('_VISPY_TESTING_BACKEND', None)
    if using is not None and using != backend:
        # e.g., we are on  a 'pyglet' run but the test requires PyQt4
        ret = (False,) if len(out) > 0 else False
        for o in out:
            ret += (None,)
        return ret
    # let's follow the standard code path
    module_name = BACKENDMAP[backend.lower()][1]
    mod = __import__('app.backends.%s' % module_name, globals(), level=2)
    mod = getattr(mod.backends, module_name)
    good = mod.testable
    for h in has:
        good = (good and getattr(mod, 'has_%s' % h))
    for cap in capable:
        good = (good and mod.capability[cap])
    ret = (good,) if len(out) > 0 else good
    for o in out:
        ret += (getattr(mod, o),)
    return ret


def requires_application(backend=None, has=(), capable=()):
    """Decorator for tests that require an application"""
    from ..app.backends import BACKEND_NAMES
    if backend is None:
        good = False
        for backend in BACKEND_NAMES:
            if has_backend(backend, has=has, capable=capable):
                good = True
                break
        msg = 'Requires application backend'
    else:
        good, why = has_backend(backend, has=has, capable=capable,
                                out=['why_not'])
        msg = 'Requires %s: %s' % (backend, why)

    # Actually construct the decorator
    def skip_decorator(f):
        import nose
        f.vispy_app_test = True  # set attribute for easy run or not

        def skipper(*args, **kwargs):
            if not good:
                raise SkipTest("Skipping test: %s: %s" % (f.__name__, msg))
            else:
                return f(*args, **kwargs)
        return nose.tools.make_decorator(f)(skipper)
    return skip_decorator


def glut_skip():
    """Helper to skip a test if GLUT is the current backend"""
    # this is basically a knownfail tool for glut
    from ..app import use_app
    app = use_app()
    if app.backend_name.lower() == 'glut':
        raise SkipTest('GLUT unstable')
    return  # otherwise it's fine


def requires_img_lib():
    """Decorator for tests that require an image library"""
    from ..util.dataio import _check_img_lib
    has_img_lib = not all(c is None for c in _check_img_lib())
    return np.testing.dec.skipif(not has_img_lib, 'imageio or PIL required')


###############################################################################
# Visuals stuff

def _has_scipy(min_version):
    try:
        import scipy  # noqa, analysis:ignore
        from distutils.version import LooseVersion
        this_version = LooseVersion(scipy.__version__)
        if this_version < min_version:
            return False
    except Exception:
        return False
    else:
        return True


def requires_scipy(min_version=0.13):
    return np.testing.dec.skipif(not _has_scipy(min_version),
                                 'Requires Scipy version >= %s' % min_version)


def assert_image_equal(image, reference):
    """Downloads reference image and compares with image

    Parameters
    ----------
    image: str, numpy.array
        'screenshot' or image data
    reference: str
        'The filename on the remote ``test-data`` repository to download'
    """
    from ..gloo.util import _screenshot
    from ..util.dataio import imread
    from ..util import get_testing_file

    if image == "screenshot":
        image = _screenshot(alpha=False)
    ref = imread(get_testing_file(reference))
    np.testing.assert_array_almost_equal(image, ref)


class TestingCanvas(Canvas):
    def __init__(self, clear_color=(0, 0, 0, 1), size=(100, 100)):
        Canvas.__init__(self, size=size)
        self._clear_color = clear_color

    def __enter__(self):
        Canvas.__enter__(self)
        from .. import gloo
        gloo.clear(color=self._clear_color)
        gloo.set_viewport(0, 0, *self.size)
        return self
