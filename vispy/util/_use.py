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

# Possible usage options. These need to be kept in sync with
# app/backends/__init__.py and the modules in gloo/gl
_app_names = 'PyQt4', 'PySide', 'Pyglet', 'Glfw', 'SDL2', 'Glut'
_gl_names = 'desktop', 'pyopengl', 'angle'


def use(usage):
    """ Set the usagage options for vispy
    
    Specify what app backend and GL backend to use. Also see
    `vispy.app.use_app()` and `vispy.gloo.gl.use_gl()`.
    
    Parameters
    ----------
    
    usage : str
        String usage options separated by spaces. Case insensitive.
    
    Options
    -------
    
    * app-options: 'PyQt4', 'PySide', 'PyGlet', 'Glfw', 'SDL2', 'Glut'
    * gl-options: 'desktop', 'pyopengl', 'angle'
    * 'debug': check for errors after each gl command.
    
    Notes
    -----
    
    If app options are given, vispy.app is imported. If gl options are
    given, vispy.gloo is imported.
    
    """
    
    # Split components of usage
    parts = set([s.lower() for s in usage.split(' ') if s])
    
    # Init things that we can set
    app_name = None
    gl_name = None
    
    # Example for future. This wont work (yet).
    if 'ipython' in parts:
        app_name = 'headless'
        gl_name = 'webgl'
    
    # Take zero or one items for app
    for name in _app_names:
        if name.lower() in parts:
            if app_name:
                raise ValueError('Can only specify one app backend.')
            app_name = name
            parts.discard(name.lower())
    
    # Take zero or one items for gl
    for name in _gl_names:
        if name.lower() in parts:
            if gl_name:
                raise ValueError('Can only specify one gl backend.')
            gl_name = name
            parts.discard(name.lower())
    
    # Gl can also be in debug mode
    if 'debug' in parts:
        gl_name += ' debug'
    parts.discard('debug')
    
    # Check if we have anything left
    if parts:
        raise ValueError('Don\'t know what to do with %r' % parts)
    
    # Apply now
    if app_name:
        import vispy.app
        vispy.app.use_app(app_name)
    if gl_name:
        import vispy.gloo
        vispy.gloo.gl.use_gl(gl_name)
