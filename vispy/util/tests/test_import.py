"""
Test that importing vispy subpackages do not pull
in any more vispy submodules than strictly necessary.
"""

import sys
import os
import subprocess

from nose.tools import assert_equal

import vispy


def check_output(*popenargs, **kwargs):
    """ Minimal py 2.6 compatible version of subprocess.check_output()

    Py2.6 does not have check_output.
    Taken from https://gist.github.com/edufelipe/1027906
    """
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        error = subprocess.CalledProcessError(retcode, cmd)
        error.output = output
        raise error
    return output


def loaded_vispy_modules(import_module, depth=None):
    """ Import the given module in subprocess and return loaded modules

    Import a certain module in a clean subprocess and return the
    vispy modules that are subsequently loaded. The given depth
    indicates the module level (i.e. depth=1 will only yield 'vispy.app'
    but not 'vispy.app.backends').
    """

    vispy_dir = os.path.dirname(os.path.dirname(vispy.__file__))

    # Get the loaded modules in a clean interpreter
    code = "import sys, %s; print(', '.join(sys.modules))" % import_module
    res = check_output([sys.executable, '-c', code], cwd=vispy_dir)
    res = res.decode('utf-8')
    loaded_modules = [name.strip() for name in res.split(',')]

    # Get only vispy modules at the given depth
    vispy_modules = set()
    for m in loaded_modules:
        if m.startswith('vispy') and not '__future__' in m:
            if depth:
                parts = m.split('.')
                m = '.'.join(parts[:depth])
            vispy_modules.add(m)

    return vispy_modules


def test_import_nothing():
    """ Not importing vispy should not import any vispy modules. """
    modnames = loaded_vispy_modules('os', 2)
    assert_equal(modnames, set())


def test_import_vispy():
    """ Importing vispy should only pull in other vispy.util submodule. """
    modnames = loaded_vispy_modules('vispy', 2)
    assert_equal(modnames, set(['vispy', 'vispy.util']))


def test_import_vispy_util():
    """ Importing vispy.util should not pull in other vispy submodules. """
    modnames = loaded_vispy_modules('vispy.util', 2)
    assert_equal(modnames, set(['vispy', 'vispy.util']))


def test_import_vispy_app():
    """ Importing vispy.app should not pull in other vispy submodules. """
    modnames = loaded_vispy_modules('vispy.app', 2)
    assert_equal(modnames, set(['vispy', 'vispy.util', 'vispy.app']))

    # todo: maybe also test that no backends are imported yet


def test_import_vispy_gloo():
    """ Importing vispy.gloo should not pull in other vispy submodules. """
    modnames = loaded_vispy_modules('vispy.gloo', 2)
    assert_equal(modnames, set(['vispy', 'vispy.util', 'vispy.gloo']))
