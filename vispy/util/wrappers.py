# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Some wrappers to avoid circular imports, or make certain calls easier.
"""

"""
The idea of a 'global' vispy.use function is that although vispy.app
and vispy.gloo.gl can be used independently, they are not complely
independent for some configureation. E.g. when using real ES 2.0,
the app backend should use EGL and not a desktop OpenGL context. Also,
we probably want it to be easy to configure vispy to use the ipython
notebook backend, which requires specifc config of both app and gl.

This module does not have to be aware of the available app and gl
backends, but it should be(come) aware of (in)compatibilities between
them.
"""

import subprocess
import inspect


def use(app=None, gl=None):
    """ Set the usage options for vispy

    Specify what app backend and GL backend to use. Also see
    ``vispy.app.use_app()`` and ``vispy.gloo.gl.use_gl()``.

    Parameters
    ----------
    app : str
        The app backend to use (case insensitive). Standard backends:
            * 'PyQt4': use Qt widget toolkit via PyQt4.
            * 'PySide': use Qt widget toolkit via PySide.
            * 'PyGlet': use Pyglet backend.
            * 'Glfw': use Glfw backend (successor of Glut). Widely available
              on Linux.
            * 'SDL2': use SDL v2 backend.
            * 'Glut': use Glut backend. Widely available but limited.
              Not recommended.
        Additional backends:
            * 'ipynb_vnc': render in the IPython notebook via a VNC approach
              (experimental)
    gl : str
        The gl backend to use (case insensitive). Options are:
            * 'desktop': use Vispy's desktop OpenGL API.
            * 'pyopengl': use PyOpenGL's desktop OpenGL API. Mostly for
              testing.
            * 'angle': (TO COME) use real OpenGL ES 2.0 on Windows via Angle.
              Availability of ES 2.0 is larger for Windows, since it relies
              on DirectX.
            * If 'debug' is included in this argument, vispy will check for
              errors after each gl command.

    Notes
    -----
    If the app option is given, ``vispy.app.use_app()`` is called. If
    the gl option is given, ``vispy.gloo.use_gl()`` is called.

    If an app backend name is provided, and that backend could not be
    loaded, an error is raised.

    If no backend name is provided, Vispy will first check if the GUI
    toolkit corresponding to each backend is already imported, and try
    that backend first. If this is unsuccessful, it will try the
    'default_backend' provided in the vispy config. If still not
    succesful, it will try each backend in a predetermined order.
    """

    # Example for future. This wont work (yet).
    if app == 'ipynb_webgl':
        app = 'headless'
        gl = 'webgl'

    # Apply now
    if app:
        import vispy.app
        vispy.app.use_app(app)
    if gl:
        import vispy.gloo
        vispy.gloo.gl.use_gl(gl)


# Define test proxy function, so we don't have to import vispy.testing always
def test(label='full', coverage=False, verbosity=1, *extra_args):
    """Test vispy software

    Parameters
    ----------
    label : str
        Can be one of 'full', 'nose', 'nobackend', 'extra', 'lineendings',
        'flake', or any backend name (e.g., 'qt').
    coverage : bool
        Produce coverage outputs (.coverage file).
    verbosity : int
        Verbosity level to use when running ``nose``.
    """
    from ..testing import _tester
    return _tester(label, coverage, verbosity, extra_args)


def run_subprocess(command):
    """Run command using subprocess.Popen

    Run command and wait for command to complete. If the return code was zero
    then return, otherwise raise CalledProcessError.
    By default, this will also add stdout= and stderr=subproces.PIPE
    to the call to Popen to suppress printing to the terminal.

    Parameters
    ----------
    command : list of str
        Command to run as subprocess (see subprocess.Popen documentation).

    Returns
    -------
    stdout : str
        Stdout returned by the process.
    stderr : str
        Stderr returned by the process.
    """
    # code adapted with permission from mne-python
    kwargs = dict(stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    p = subprocess.Popen(command, **kwargs)
    stdout_, stderr = p.communicate()

    output = (stdout_, stderr)
    if p.returncode:
        print(stdout_)
        print(stderr)
        err_fun = subprocess.CalledProcessError.__init__
        if 'output' in inspect.getargspec(err_fun).args:
            raise subprocess.CalledProcessError(p.returncode, command, output)
        else:
            raise subprocess.CalledProcessError(p.returncode, command)

    return output
