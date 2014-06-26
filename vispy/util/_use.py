# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" 
## Motivation

The idea of a 'global' vispy.use function is that although vispy.app
and vispy.gloo.gl can be used independently, they are not complely
independent for some configureation. E.g. when using real ES 2.0,
the app backend should use EGL and not a desktop OpenGL context. Also,
we probably want it to be easy to configure vispy to use the ipython
notebook backend, which requires specifc config of both app and gl.


## Implementation

The user specifies a string with usage options. In that way we can
easily add special modes of operation like 'inb' for the IPython
notebook. The use functions evaluates the string and should know what
to do with it. It should raise an error if an invalid usage option is
given. Therefore, this module should be aware of the possible usage
modes for app and gl. 

"""


# Define backends: name, vispy.app.backends.xxx module, native module name.
# This is the order in which they are attempted to be imported.
APP_BACKENDS = [
    ('PyQt4', '_pyqt4', 'PyQt4'),
    ('PySide', '_pyside', 'PySide'),
    ('Pyglet', '_pyglet', 'pyglet'),
    ('Glfw', '_glfw', 'vispy.app.backends._libglfw'),
    ('SDL2', '_sdl2', 'sdl2'),
    ('Glut', '_glut', 'OpenGL.GLUT'),
    ('_test', '_test', 'vispy.app.backends._test'),  # add one that will fail
]

APP_BACKEND_NAMES = []
for backend in APP_BACKENDS:
    if backend[1][1:] not in APP_BACKEND_NAMES:  # remove redundant qt entries
        APP_BACKEND_NAMES.append(backend[1][1:])

# Map of the lowercase backend names to the backend descriptions above
# so that we can look up its properties if we only have a name.
APP_BACKENDMAP = dict([(be[0].lower(), be) for be in APP_BACKENDS])


# Define possible GL backends
GL_BACKENDS = 'desktop', 'pyopengl', 'angle'


def use(app=None, gl=None):
    """ Set the usage options for vispy
    
    Specify what app backend and GL backend to use. Also see
    ``vispy.app.use_app()`` and ``vispy.gloo.gl.use_gl()``.
    
    Parameters
    ----------
    app : str
        The app backend to use (case insensitive). Options are:
        * 'PyQt4': use Qt widget toolkit via PyQt4.
        * 'PySide': use Qt widget toolkit via PySide.
        * 'PyGlet': use Pyglet backend.
        * 'Glfw': use Glfw backend (successor of Glut). Widely available
            on Linux.
        * 'SDL2': use SDL v2 backend.
        * 'Glut': use Glut backend. Widely available but limited. 
            Not recommended.
        In the future, we plan on providing 'special' app backends such
        as 'ipynb' to run vispy in the IPython notebook.
    gl : str
        The gl backend to use (case insensitive). Options are:
        * 'desktop': use Vispy's desktop OpenGL API. 
        * 'pyopengl': use PyOpenGL's desktop OpenGL API. Mostly for testing.
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
    if app == 'ipynb':
        app = 'headless'
        gl = 'webgl'
    
    # Apply now
    if app:
        import vispy.app
        vispy.app.use_app(app)
    if gl:
        import vispy.gloo
        vispy.gloo.gl.use_gl(gl)
