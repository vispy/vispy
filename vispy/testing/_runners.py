"""Test running functions"""

from __future__ import print_function

import sys
import os
from os import path as op
from subprocess import Popen
from copy import deepcopy
from functools import partial

from ..util.ptime import time
from ._testing import SkipTest, has_backend


def _get_root_dir():
    root_dir = os.getcwd()
    if (op.isfile(op.join(root_dir, 'setup.py')) and
            op.isdir(op.join(root_dir, 'vispy'))):
        dev = True
    else:
        root_dir = op.abspath(op.join(op.dirname(__file__), '..', '..'))
        dev = True if op.isfile(op.join(root_dir, 'setup.py')) else False
    return root_dir, dev


def _nose(mode, verbosity, coverage):
    """Run nosetests using a particular mode"""
    cwd = os.getcwd()  # this must be done before nose import
    try:
        import nose  # noqa, analysis:ignore
    except ImportError:
        print('Skipping nosetests, nose not installed')
        raise SkipTest()
    extra = ('-' * 70)
    if mode == 'nobackend':
        print(extra + '\nRunning tests with no backend')
        attrs = '-a !vispy_app_test '
    else:
        has, why_not = has_backend(mode, out=['why_not'])
        if has:
            print('%s\nRunning tests with %s backend' % (extra, mode))
            attrs = '-a vispy_app_test '
        else:
            msg = ('Skipping tests for backend %s, not found (%s)'
                   % (mode, why_not))
            print(extra + '\n' + msg + '\n' + extra + '\n')  # last \n nicer
            raise SkipTest(msg)
    sys.stdout.flush()
    if coverage:
        covs = '--with-coverage --cover-package=vispy --cover-branches '
    else:
        covs = ''
    args = ' ' + ('--verbosity=%s ' % verbosity) + covs + attrs
    # make a call to "python" so that it inherits whatever the system
    # thinks is "python" (e.g., virtualenvs)
    cmd = ['python', '-c',
           'import nose; nose.main(argv="%s".split(" "))' % args]
    env = deepcopy(os.environ)
    env.update(dict(_VISPY_TESTING_TYPE=mode))
    p = Popen(cmd, cwd=cwd, env=env)
    stdout, stderr = p.communicate()
    if(p.returncode):
        raise RuntimeError('Nose failure (%s):\n%s' % (p.returncode, stderr))


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


def _tester(label='full', coverage=False, verbosity=1):
    """Test vispy software

    Parameters
    ----------
    label : str
        Can be one of 'full', 'nose', 'nobackend', 'extra', 'lineendings',
        'flake', or any backend name (e.g., 'qt').
    coverage : bool
        Produce coverage outputs (.coverage file and printing).
    verbosity : int
        Verbosity level to use when running ``nose``.
    """
    from vispy.app.backends import BACKEND_NAMES as backend_names
    label = label.lower()
    verbosity = int(verbosity)
    cov = bool(coverage)
    if cov and op.isfile('.coverage'):
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
            runs.append([partial(_nose, backend, verbosity, cov), backend])
    elif label in backend_names:
        runs.append([partial(_nose, label, verbosity, cov), label])
    if label in ('full', 'nose', 'nobackend'):
        runs.append([partial(_nose, 'nobackend', verbosity, cov), 'nobackend'])
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
        except Exception as exp:
            # this should only happen if we've screwed up the test setup
            fail += [run[1]]
            print('Failed strangely: %s\n' % str(exp))
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
