# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Test that importing vispy subpackages do not pull
in any more vispy submodules than strictly necessary.
"""

import sys
import os

from vispy.testing import (assert_in, assert_not_in, requires_pyopengl,
                           run_tests_if_main, assert_equal)
from vispy.util import run_subprocess
import vispy


# minimum that will be imported when importing vispy
_min_modules = ['vispy', 'vispy.util', 'vispy.ext', 'vispy.testing']


def loaded_vispy_modules(import_module, depth=None, all_modules=False):
    """ Import the given module in subprocess and return loaded modules

    Import a certain module in a clean subprocess and return the
    vispy modules that are subsequently loaded. The given depth
    indicates the module level (i.e. depth=1 will only yield 'vispy.app'
    but not 'vispy.app.backends').
    """

    vispy_dir = os.path.dirname(os.path.dirname(vispy.__file__))

    # Get the loaded modules in a clean interpreter
    code = "import sys, %s; print(', '.join(sys.modules))" % import_module
    res = run_subprocess([sys.executable, '-c', code], cwd=vispy_dir)[0]
    loaded_modules = [name.strip() for name in res.split(',')]

    if all_modules:
        return loaded_modules

    # Get only vispy modules at the given depth
    vispy_modules = set()
    for m in loaded_modules:
        if m.startswith('vispy') and '__future__' not in m:
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
    assert_equal(modnames, set(_min_modules))


def test_import_vispy_util():
    """ Importing vispy.util should not pull in other vispy submodules. """
    modnames = loaded_vispy_modules('vispy.util', 2)
    assert_equal(modnames, set(_min_modules))


def test_import_vispy_app1():
    """ Importing vispy.app should not pull in other vispy submodules. """
    # Since the introduction of the GLContext to gloo, app depends on gloo
    modnames = loaded_vispy_modules('vispy.app', 2)
    assert_equal(modnames, set(_min_modules + ['vispy.app', 'vispy.gloo',
                                               'vispy.glsl', 'vispy.color']))


def test_import_vispy_app2():
    """ Importing vispy.app should not pull in any backend toolkit. """
    allmodnames = loaded_vispy_modules('vispy.app', 2, True)
    assert_not_in('PySide', allmodnames)
    assert_not_in('PyQt4', allmodnames)
    assert_not_in('pyglet', allmodnames)


def test_import_vispy_gloo():
    """ Importing vispy.gloo should not pull in other vispy submodules. """
    modnames = loaded_vispy_modules('vispy.gloo', 2)
    assert_equal(modnames, set(_min_modules + ['vispy.gloo',
                                               'vispy.glsl',
                                               'vispy.color']))


def test_import_vispy_no_pyopengl():
    """ Importing vispy.gloo.gl.gl2 should not import PyOpenGL. """
    # vispy.gloo desktop backend
    allmodnames = loaded_vispy_modules('vispy.gloo.gl.gl2', 2, True)
    assert_not_in('OpenGL', allmodnames)
    # vispy.app 
    allmodnames = loaded_vispy_modules('vispy.app', 2, True)
    assert_not_in('OpenGL', allmodnames)
    # vispy.scene
    allmodnames = loaded_vispy_modules('vispy.scene', 2, True)
    assert_not_in('OpenGL', allmodnames)


@requires_pyopengl()
def test_import_vispy_pyopengl():
    """ Importing vispy.gloo.gl.pyopengl2 should import PyOpenGL. """
    allmodnames = loaded_vispy_modules('vispy.gloo.gl.pyopengl2', 2, True)
    assert_in('OpenGL', allmodnames)


def test_import_vispy_scene():
    """ Importing vispy.gloo.gl.desktop should not import PyOpenGL. """
    modnames = loaded_vispy_modules('vispy.scene', 2)
    more_modules = ['vispy.app', 'vispy.gloo', 'vispy.glsl', 'vispy.scene', 
                    'vispy.color', 
                    'vispy.io', 'vispy.geometry', 'vispy.visuals']
    assert_equal(modnames, set(_min_modules + more_modules))


run_tests_if_main()
