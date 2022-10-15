# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import os
from packaging.version import Version

from vispy.util import use_log_level


def has_matplotlib(version='1.2'):
    """Determine if mpl is a usable version"""
    try:
        import matplotlib
    except Exception:
        has_mpl = False
    else:
        if Version(matplotlib.__version__) >= Version(version):
            has_mpl = True
        else:
            has_mpl = False
    return has_mpl


def has_skimage(version='0.11'):
    """Determine if scikit-image is a usable version"""
    try:
        import skimage
    except ImportError:
        return False
    sk_version = Version(skimage.__version__)
    return sk_version >= Version(version)


def has_backend(backend, has=(), capable=(), out=()):
    from ..app.backends import BACKENDMAP
    using = os.getenv('_VISPY_TESTING_APP', None)
    if using is not None and using != backend:
        # e.g., we are on  a 'pyglet' run but the test requires PyQt4
        ret = (False,) if len(out) > 0 else False
        for o in out:
            ret += (None,)
        return ret

    # let's follow the standard code path
    module_name = BACKENDMAP[backend.lower()][1]
    with use_log_level('warning', print_msg=False):
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
