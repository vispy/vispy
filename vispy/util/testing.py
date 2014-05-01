# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from __future__ import print_function

import numpy as np
import os
from os import path as op
import sys
from subprocess import Popen
from copy import deepcopy
from functools import partial
try:
    from unittest.case import SkipTest
except ImportError:
    try:
        from unittest2.case import SkipTest
    except ImportError:
        class SkipTest(Exception):
            pass

from .ptime import time


###############################################################################
# Adapted from Python's unittest2 (which is wrapped by nose)
# http://docs.python.org/2/license.html

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
    using = os.getenv('_VISPY_TESTING_BACKEND', None)
    if using is not None and using != backend:
        ret = (False,) if len(out) > 0 else False
        for o in out:
            ret += (None,)
    else:
        mod = __import__('app.backends._%s' % backend, globals(), level=2)
        mod = getattr(mod.backends, '_%s' % backend)
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


###############################################################################
# Test running

def _get_root_dir():
    root_dir = os.getcwd()
    if (op.isfile(op.join(root_dir, 'setup.py')) and
            op.isdir(op.join(root_dir, 'vispy'))):
        dev = True
    else:
        root_dir = op.abspath(op.join(op.dirname(__file__), '..', '..'))
        dev = True if op.isfile(op.join(root_dir, 'setup.py')) else False
    return root_dir, dev


def _tester(label='full'):
    """Test vispy software

    Parameters
    ----------
    label : str
        Can be one of 'full', 'nose', 'nobackend', 'extra', 'lineendings',
        'flake', or any backend name (e.g., 'qt').
    """
    from vispy.app.backends import BACKEND_NAMES as backend_names
    label = label.lower()
    if op.isfile('.coverage'):
        os.remove('.coverage')
    known_types = ['full', 'nose', 'lineendings', 'extra', 'flake',
                   'nobackend'] + backend_names
    if label not in known_types:
        raise ValueError('label must be one of %s, or a backend name %s'
                         % (known_types, backend_names))
    work_dir = _get_root_dir()[0]
    orig_dir = os.getcwd()
    # figure out what we actually need to run
    runs = []
    if label in ('full', 'nose'):
        for backend in backend_names:
            runs.append([partial(_nose, backend), backend])
    elif label in backend_names:
        runs.append([partial(_nose, label), label])
    if label in ('full', 'nose', 'nobackend'):
        runs.append([partial(_nose, 'nobackend'), 'nobackend'])
    if label in ('full', 'extra', 'lineendings'):
        runs.append([_check_line_endings, 'lineendings'])
    if label in ('full', 'extra', 'flake'):
        runs.append([_flake, 'flake'])
    t0 = time()
    fail = []
    skip = []
    for run in runs:
        try:
            os.chdir(work_dir)
            run[0]()
        except RuntimeError:
            print('Failed')
            fail += [run[1]]
        except SkipTest:
            skip += [run[1]]
        else:
            print('Passed')
        finally:
            sys.stdout.flush()
            os.chdir(orig_dir)
    dt = time() - t0
    stat = '%s failed, %s skipped' % (fail if fail else 0, skip if skip else 0)
    extra = 'failed' if fail else 'succeeded'
    print('Testing %s (%s) in %0.3f seconds' % (extra, stat, dt))
    sys.stdout.flush()
    if len(fail) > 0:
        raise RuntimeError('FAILURE')


def _nose(mode):
    """Run nosetests using a particular mode"""
    try:
        import nose  # noqa, analysis:ignore
    except ImportError:
        print('Skipping nosetests, nose not installed')
        raise SkipTest()
    if mode == 'nobackend':
        print('Running tests with no backend')
        attrs = ['-a', '!vispy_app_test']
    elif has_backend(mode):
        print('Running tests with %s backend' % mode)
        attrs = ['-a', 'vispy_app_test']
    else:
        print('Skipping tests for backend %s, not found' % mode)
        raise SkipTest()
    sys.stdout.flush()
    cmd = ['nosetests', '-d', '--with-coverage', '--cover-package=vispy',
           '--cover-branches', '--verbosity=2'] + attrs
    env = deepcopy(os.environ)
    env.update(dict(_VISPY_TESTING_TYPE=mode))
    proc = Popen(cmd, env=env)
    stdout, stderr = proc.communicate()
    if(proc.returncode):
        raise RuntimeError('Nose failure (%s):\n%s'
                           % (proc.returncode, stderr))


def _flake():
    """Test flake8"""
    orig_dir = os.getcwd()
    root_dir, dev = _get_root_dir()
    os.chdir(root_dir)
    if dev:
        sys.argv[1:] = ['vispy', 'examples', 'make']
    else:
        sys.argv[1:] = ['vispy']
    sys.argv.append('--ignore=E226,E241,E265,W291,W293')
    sys.argv.append('--exclude=six.py,_py24_ordereddict.py,_libglfw.py,'
                    '_proxy.py,_angle.py,_desktop.py,_pyopengl.py,'
                    '_constants.py')
    try:
        from flake8.main import main
    except ImportError:
        print('Skipping flake8 test, flake8 not installed')
    else:
        print('Running flake8... ')  # if end='', first error gets ugly
        sys.stdout.flush()
        try:
            main()
        except SystemExit as ex:
            if ex.code in (None, 0):
                pass  # do not exit yet, we want to print a success msg
            else:
                raise RuntimeError('flake8 failed')
    finally:
        os.chdir(orig_dir)


def _check_line_endings():
    """Check all files in the repository for CR characters"""
    print('Running line endings check... ', end='')
    sys.stdout.flush()
    report = []
    root_dir, dev = _get_root_dir()
    if not dev:
        root_dir = op.join(root_dir, 'vispy')
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for fname in filenames:
            if op.splitext(fname)[1] in ('.pyc', '.pyo', '.so', '.dll'):
                continue
            # Get filename
            filename = op.join(dirpath, fname)
            relfilename = op.relpath(filename, root_dir)
            # Open and check
            try:
                text = open(filename, 'rb').read().decode('utf-8')
            except UnicodeDecodeError:
                continue  # Probably a binary file
            crcount = text.count('\r')
            if crcount:
                lfcount = text.count('\n')
                report.append('In %s found %i/%i CR/LF' %
                              (relfilename, crcount, lfcount))

    # Process result
    if len(report) > 0:
        raise RuntimeError('Found %s files with incorrect endings:\n%s'
                           % (len(report), '\n'.join(report)))
