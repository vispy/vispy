# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" 
Implements the global singleton app object.

"""

from __future__ import print_function, division, absolute_import

import sys

import vispy
from vispy.app.backends import BACKENDS, BACKENDMAP, ATTEMPTED_BACKENDS



class Application(object):
    """ Representation of the vispy application. This wraps a native 
    GUI application instance. Vispy has a default instance of this class
    at vispy.app.default_app.
    
    There are multiple stages for an Application object:
        * Backend-less - the state when it is just initialized
        * Backend selected - use() has been successfully called. Note that
          the Canvas calls use() without arguments reight before creating
          its backend widget.
        * Native application is created - the Canvas probes the 
          Application,native property to ensure that there is a native 
          application right before a native widget is created.
    
    """
    
    def __init__(self):
        self._backend_module = None
        self._backend = None
    
    def __repr__(self):
        name = self.backend_name
        if not name:
            return '<Vispy app with no backend>'
        else:
            return '<Vispy app, wrapping the %s GUI toolkit>' % name
    
    @property
    def backend_name(self):
        """ The name of the GUI backend that this app wraps.
        """
        if self._backend is not None:
            return self._backend._vispy_get_backend_name()
        else:
            return ''
    
    @property
    def backend_module(self):
        """ The module object that defines the backend.
        """
        return self._backend_module
    
    def process_events(self):
        """ Process all pending GUI events. If the mainloop is not
        running, this should be done regularly to keep the visualization
        interactive and to keep the event system going.
        """
        return self._backend._vispy_process_events()
    
    def run(self):
        """ Enter the native GUI event loop. 
        """
        return self._backend._vispy_run()
    
    def quit(self):
        """ Quit the native GUI event loop.
        """
        return self._backend._vispy_quit()
    
    @property
    def native(self):
        """ The native GUI application instance.
        """
        return self._backend._vispy_get_native_app()

    
    def use(self, backend_name=None):
        """ Select a backend by name. If the backend name is omitted,
        will chose a suitable backend automatically. It is an error to
        try to select a particular backend if one is already selected.
        Available backends: 'PySide', 'PyQt4', 'Glut', 'Pyglet', 'qt'. 
        The latter will use PySide or PyQt4, whichever works.
        
        If a backend name is provided, and that backend could not be 
        loaded, an error is raised.
        
        If no backend name is provided, this function will first check
        if the GUI toolkit corresponding to each backend is already
        imported, and try that backend first. If this is unsuccessful,
        it will try the 'default_backend' provided in the vispy config.
        If still not succesful, it will try each backend in a
        predetermined order.
        
        """
        import vispy.app
        
        # Should we try and load any backend, or just this specific one?
        try_others = backend_name is None
        
        # Check if already selected
        if self._backend is not None:
            if backend_name and backend_name.lower() != self.backend_name.lower():
                raise RuntimeError('Can only select a backend once.')
            return
        
        
        # Get backends to try ...
        backends_to_try = []
        if not try_others:
            # Test if given name is ok
            if backend_name.lower() not in BACKENDMAP.keys():
                raise ValueError('Backend name not known: "%s"' % backend_name)
            # Add it
            backends_to_try.append(backend_name.lower())
        else:
            # See if a backend is loaded
            for name, module_name, native_module_name in BACKENDS:
                if native_module_name and native_module_name in sys.modules:
                    backends_to_try.append(name.lower())
            # See if a default is given
            default_backend = vispy.config['default_backend'].lower()
            if default_backend.lower() in BACKENDMAP.keys():
                if default_backend not in backends_to_try:
                    backends_to_try.append(default_backend)
            # After this, try each one
            for name, module_name, native_module_name in BACKENDS:
                name = name.lower()
                if name not in backends_to_try:
                    backends_to_try.append(name)
        
        
        # Now try each one
        for key in backends_to_try:
            # Get info for this backend
            try:
                name, module_name, native_module_name = BACKENDMAP[key]
            except KeyError:
                print('This should not happen, unknown backend: "".' % key)
                continue
            # Get backend module name
            mod_name = 'vispy.app.backends.' + module_name
            # Try to import it ...
            try:
                ATTEMPTED_BACKENDS.append(name)
                __import__(mod_name)
            except ImportError as err:
                msg = 'Could not import backend "%s":\n%s' % (name, str(err))
                if not try_others:
                    raise RuntimeError(msg)
            except Exception as err:
                msg = 'Error while importing backend "%s":\n%s' % (name, str(err))
                if not try_others:
                    raise RuntimeError(msg)
                else:
                    print(msg)
            else:
                # Success!
                self._backend_module = getattr(vispy.app.backends, module_name)
                break
        else:
            raise RuntimeError('Could not import any of the backends.')
        
        # Store classes for app backend and canvas backend 
        self._backend = self.backend_module.ApplicationBackend()


class ApplicationBackend(object):
    """ ApplicationBackend()
    
    Abstract class that provides an interface between backends and Application.
    Each backend must implement a subclass of ApplicationBackend, and
    implement all its _vispy_xxx methods.
    """
    
    def _vispy_get_backend_name(self):
        raise NotImplementedError()
    
    def _vispy_process_events(self):
        raise NotImplementedError()
    
    def _vispy_run(self):
        raise NotImplementedError()
    
    def _vispy_quit(self):
        raise NotImplementedError()
    
    def _vispy_get_native_app(self):
        # Should return the native application object
        return self

