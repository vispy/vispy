# -*- coding: utf-8 -*-
# vispy: testskip
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""Test running functions"""

from __future__ import print_function

import sys
import os
from os import path as op
from copy import deepcopy
from functools import partial

from ..util import use_log_level, run_subprocess
from ..util.ptime import time
from ._testing import SkipTest, has_backend, has_application, nottest


_line_sep = '-' * 70


def _get_root_dir():
    root_dir = os.getcwd()
    if (op.isfile(op.join(root_dir, 'setup.py')) and
            op.isdir(op.join(root_dir, 'vispy'))):
        dev = True
    else:
        root_dir = op.abspath(op.join(op.dirname(__file__), '..', '..'))
        dev = True if op.isfile(op.join(root_dir, 'setup.py')) else False
    return root_dir, dev


_nose_script = """
# Code inspired by original nose plugin:
# https://nose.readthedocs.org/en/latest/plugins/cover.html

import nose
from nose.plugins.base import Plugin


class MutedCoverage(Plugin):
    '''Make a silent coverage report using Ned Batchelder's coverage module.'''

    def configure(self, options, conf):
        Plugin.configure(self, options, conf)
        self.enabled = True
        try:
            from coverage import coverage
        except ImportError:
            self.enabled = False
            self.cov = None
            print('Module "coverage" not installed, code coverage will not '
                  'be available')
        else:
            self.enabled = True
            self.cov = coverage(auto_data=False, branch=True, data_suffix=None,
                                source=['vispy'])

    def begin(self):
        self.cov.load()
        self.cov.start()

    def report(self, stream):
        self.cov.stop()
        self.cov.combine()
        self.cov.save()


try:
    import faulthandler
    faulthandler.enable()
except Exception:
    pass

nose.main(argv=%r%s)
"""


def _nose(mode, extra_arg_string):
    """Run nosetests using a particular mode"""
    cwd = os.getcwd()  # this must be done before nose import
    try:
        import nose  # noqa, analysis:ignore
    except ImportError:
        print('Skipping nosetests, nose not installed')
        raise SkipTest()

    if mode == 'nobackend':
        msg = 'Running tests with no backend'
        extra_arg_string = '-a !vispy_app_test ' + extra_arg_string
        extra_arg_string = '-e experimental -e wiki ' + extra_arg_string
        coverage = True
    elif mode == 'singlefile':
        fname = extra_arg_string.split(' ')[0]
        assert op.isfile(fname)
        msg = 'Running tests for individual file'
        coverage = False
    else:
        with use_log_level('warning', print_msg=False):
            has, why_not = has_backend(mode, out=['why_not'])
        if not has:
            msg = ('Skipping tests for backend %s, not found (%s)'
                   % (mode, why_not))
            print(_line_sep + '\n' + msg + '\n' + _line_sep + '\n')
            raise SkipTest(msg)
        msg = 'Running tests with %s backend' % mode
        extra_arg_string = '-a vispy_app_test ' + extra_arg_string
        coverage = True
    coverage = ', addplugins=[MutedCoverage()]' if coverage else ''
    args = ['nosetests'] + extra_arg_string.strip().split(' ')
    # make a call to "python" so that it inherits whatever the system
    # thinks is "python" (e.g., virtualenvs)
    cmd = [sys.executable, '-c', _nose_script % (args, coverage)]
    env = deepcopy(os.environ)
    if mode in ('singlefile',):
        env_str = ''
    else:
        # We want to set this for all app backends plus "nobackend" to
        # help ensure that app tests are appropriately decorated
        env.update(dict(_VISPY_TESTING_APP=mode))
        env_str = '_VISPY_TESTING_APP=%s ' % mode
    if len(msg) > 0:
        msg = ('%s\n%s:\n%s%s'
               % (_line_sep, msg, env_str, ' '.join(args)))
        print(msg)
    sys.stdout.flush()
    return_code = run_subprocess(cmd, return_code=True, cwd=cwd, env=env,
                                 stdout=None, stderr=None)[2]
    if return_code:
        raise RuntimeError('Nose failure (%s)' % return_code)


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
    sys.argv.append('--exclude=six.py,py24_ordereddict.py,glfw.py,'
                    '_proxy.py,_es2.py,_desktop.py,_pyopengl.py,'
                    '_constants.py,png.py,decorator.py,ipy_inputhook.py,'
                    'experimental,wiki,_old')
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
    if sys.platform == 'win32':
        print('Skipping line endings check on Windows')
        sys.stdout.flush()
        return
    print('Running line endings check... ')
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
                with open(filename, 'rb') as fid:
                    text = fid.read().decode('utf-8')
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


_script = """
import sys
import time
import warnings
try:
    import faulthandler
    faulthandler.enable()
except Exception:
    pass
import {0}

if hasattr({0}, 'canvas'):
    canvas = {0}.canvas
elif hasattr({0}, 'Canvas'):
    canvas = {0}.Canvas()
else:
    raise RuntimeError('Bad example formatting: fix or add to exclude list')

with canvas as c:
    for _ in range(5):
        c.update()
        c.app.process_events()
        time.sleep(1./60.)
"""


def _examples():
    """Run all examples and make sure they work
    """
    root_dir, dev = _get_root_dir()
    reason = None
    if not dev:
        reason = 'Cannot test examples unless in vispy git directory'
    else:
        with use_log_level('warning', print_msg=False):
            good, backend = has_application(capable=('multi_window',))
        if not good:
            reason = 'Must have suitable app backend'
    if reason is not None:
        msg = 'Skipping example test: %s' % reason
        print(msg)
        raise SkipTest(msg)
    fnames = [op.join(d[0], fname)
              for d in os.walk(op.join(root_dir, 'examples'))
              for fname in d[2] if fname.endswith('.py')]
    fnames = sorted(fnames, key=lambda x: x.lower())
    print(_line_sep + '\nRunning %s examples using %s backend'
          % (len(fnames), backend))
    op.join('tutorial', 'app', 'shared_context.py'),  # non-standard

    fails = []
    n_ran = n_skipped = 0
    t0 = time()
    for fname in fnames:
        n_ran += 1
        root_name = op.split(fname)
        root_name = op.join(op.split(op.split(root_name[0])[0])[1],
                            op.split(root_name[0])[1], root_name[1])
        good = True
        with open(fname, 'r') as fid:
            for _ in range(10):  # just check the first 10 lines
                line = fid.readline()
                if line == '':
                    break
                elif line.startswith('# vispy: ') and 'testskip' in line:
                    good = False
                    break
        if not good:
            n_ran -= 1
            n_skipped += 1
            continue
        sys.stdout.flush()
        cwd = op.dirname(fname)
        cmd = [sys.executable, '-c', _script.format(op.split(fname)[1][:-3])]
        sys.stdout.flush()
        stdout, stderr, retcode = run_subprocess(cmd, return_code=True,
                                                 cwd=cwd, env=os.environ)
        if retcode or len(stderr.strip()) > 0:
            ext = '\n' + _line_sep + '\n'
            fails.append('%sExample %s failed (%s):%s%s%s'
                         % (ext, root_name, retcode, ext, stderr, ext))
            print(fails[-1])
        else:
            print('.', end='')
        sys.stdout.flush()
    print('')
    t = (': %s failed, %s succeeded, %s skipped in %s seconds'
         % (len(fails), n_ran - len(fails), n_skipped, round(time()-t0)))
    if len(fails) > 0:
        raise RuntimeError('Failed%s' % t)
    print('Success%s' % t)


@nottest
def test(label='full', extra_arg_string=''):
    """Test vispy software

    Parameters
    ----------
    label : str
        Can be one of 'full', 'nose', 'nobackend', 'extra', 'lineendings',
        'flake', or any backend name (e.g., 'qt').
    extra_arg_string : str
        Extra arguments to sent to ``nose``, e.g. ``'-x --verbosity=2'``.
    """
    from vispy.app.backends import BACKEND_NAMES as backend_names
    label = label.lower()
    if op.isfile('.coverage'):
        os.remove('.coverage')
    known_types = ['full', 'nose', 'lineendings', 'extra', 'flake',
                   'nobackend', 'examples'] + backend_names
    if label not in known_types:
        raise ValueError('label must be one of %s, or a backend name %s'
                         % (known_types, backend_names))
    work_dir = _get_root_dir()[0]
    orig_dir = os.getcwd()
    # figure out what we actually need to run
    runs = []
    if label in ('full', 'nose'):
        for backend in backend_names:
            runs.append([partial(_nose, backend, extra_arg_string),
                         backend])
    elif label in backend_names:
        runs.append([partial(_nose, label, extra_arg_string), label])
    if label in ('full', 'examples'):
        runs.append([_examples, 'examples'])
    if label in ('full', 'nose', 'nobackend'):
        runs.append([partial(_nose, 'nobackend', extra_arg_string),
                     'nobackend'])
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
        except RuntimeError as exp:
            print('Failed: %s' % str(exp))
            fail += [run[1]]
        except SkipTest:
            skip += [run[1]]
        except Exception as exp:
            # this should only happen if we've screwed up the test setup
            fail += [run[1]]
            print('Failed strangely (%s): %s\n' % (type(exp), str(exp)))
            import traceback
            type_, value, tb = sys.exc_info()
            traceback.print_exception(type_, value, tb)
        else:
            print('Passed\n')
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
