# -*- coding: utf-8 -*-
""" 
Implements the global singleton app object.

"""

from __future__ import print_function, division, absolute_import

import pyvis



class App(object):
    """ Representation of the pyvis application. There is always exactly
    one pyvis app object, and it wraps a native GUI application
    instance.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
    """
    
    def __init__(self):
        self._backend = None
    
    def __repr__(self):
        name = self.backend_name
        if not name:
            return '<The pyvis app with no backend>'
        else:
            return '<The pyvis app, wrapping the %s GUI toolkit>' % name
    
    @property
    def backend_name(self):
        """ The name of the GUI backend that this app wraps.
        """
        if self._backend is not None:
            return self._backend._pyvis_get_backend_name()
        else:
            return ''
    
    def process_events(self):
        """ Process all pending GUI events. If the mainloop is not
        running, this should be done regularly to keep the visualization
        interactive and to keep the event system going.
        """
        return self._backend._pyvis_process_events()
    
    def run(self):
        """ Enter the native GUI event loop. 
        """
        return self._backend._pyvis_run()
    
    def quit(self):
        """ Quit the native GUI event loop.
        """
        return self._backend._pyvis_quit()
    
    @property
    def native_app(self):
        """ The native GUI application instance.
        """
        return self._backend._pyvis_get_native_app()

    
    def use(self, backend_name=None):
        """ Select a backend by name. If the backend name is omitted,
        will chose a suitable backend automatically.
        """
        import pyvis.canvas
        
        # Check if already selected
        if backend_name and self._backend is not None:
            raise RuntimeError('Can only select a backend once.')
        
        if backend_name is None:
            backend_name = pyvis.config['default_backend']
        
        # Get backend module
        mod_name = 'pyvis.canvas.backends.' + backend_name
        __import__(mod_name)
        self._backendModule = getattr(pyvis.canvas.backends, backend_name)
        
        # Store classes for app backend and canvas backend 
        # todo: this only works for Qt now
        self._CanvasBackend = self._backendModule.QtCanvasBackend
        self._AppBackend = self._backendModule.QtAppBackend
        self._backend = self._AppBackend()


class AppBackend(object):
    """ Backends should implement this.
    """
    
    def _pyvis_get_backend_name(self):
        raise NotImplementedError()
    
    def _pyvis_process_events(self):
        raise NotImplementedError()
    
    def _pyvis_run(self):
        raise NotImplementedError()
    
    def _pyvis_quit(self):
        raise NotImplementedError()
    
    def _pyvis_get_native_app(self):
        raise NotImplementedError()
    
    