# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""Implements the global singleton app object."""

from __future__ import division

import builtins
import os
import sys

from . import backends
from .backends import CORE_BACKENDS, BACKEND_NAMES, BACKENDMAP, TRIED_BACKENDS
from .. import config
from .base import BaseApplicationBackend as ApplicationBackend  # noqa
from ._detect_eventloop import _get_running_interactive_framework
from ..util import logger


class Application(object):
    """Representation of the vispy application

    This wraps a native GUI application instance. Vispy has a default
    instance of this class that can be created/obtained via
    `vispy.app.use_app()`.

    Parameters
    ----------
    backend_name : str | None
        The name of the backend application to use. If not specified,
        Vispy tries to select a backend automatically. See ``vispy.use()``
        for details.

    Notes
    -----
    Upon creating an Application object, a backend is selected, but the
    native backend application object is only created when `create()`
    is called or `native` is used. The Canvas and Timer do this
    automatically.

    """

    def __init__(self, backend_name=None):
        self._backend_module = None
        self._backend = None
        self._use(backend_name)

    def __repr__(self):
        name = self.backend_name
        if not name:
            return '<Vispy app with no backend>'
        else:
            return '<Vispy app, wrapping the %s GUI toolkit>' % name

    @property
    def backend_name(self):
        """The name of the GUI backend that this app wraps."""
        if self._backend is not None:
            return self._backend._vispy_get_backend_name()
        else:
            return ''

    @property
    def backend_module(self):
        """The module object that defines the backend."""
        return self._backend_module

    def process_events(self):
        """Process all pending GUI events. If the mainloop is not
        running, this should be done regularly to keep the visualization
        interactive and to keep the event system going.
        """
        return self._backend._vispy_process_events()

    def sleep(self, duration_sec):
        """Sleep for the given duration in seconds.

        This is used to reduce
        CPU stress when VisPy is run in interactive mode.

        Parameters
        ----------
        duration_sec: float
            Time to sleep in seconds
        """
        self._backend._vispy_sleep(duration_sec)

    def create(self):
        """Create the native application."""
        # Ensure that the native app exists
        self.native

    def is_interactive(self):
        """Determine if the user requested interactive mode."""
        # The Python interpreter sets sys.flags correctly, so use them!
        if sys.flags.interactive:
            return True

        # IPython does not set sys.flags when -i is specified, so first
        # check it if it is already imported.
        if not hasattr(builtins, '__IPYTHON__'):
            return False

        # Then we check the application singleton and determine based on
        # a variable it sets.
        try:
            try:
                # ipython >=3.0
                from traitlets.config.application import Application as App
            except ImportError:
                # ipython <3.0
                from IPython.config.application import Application as App
            return App.initialized() and App.instance().interact
        except (ImportError, AttributeError):
            return False

    def is_notebook(self):
        """Determine if the user is executing in a Jupyter Notebook"""
        try:
            # 'get_ipython' is available in globals when running from
            # IPython/Jupyter
            ip = get_ipython()
            if ip.has_trait('kernel'):
                # There doesn't seem to be an easy way to detect the frontend
                # That said, if using a kernel, the user can choose to have an
                # event loop, we therefore make sure the event loop isn't
                # specified before assuming it is a notebook
                # https://github.com/vispy/vispy/issues/1708
                # https://github.com/ipython/ipython/issues/11920
                return _get_running_interactive_framework() is None
            else:
                # `jupyter console` is used
                return False
        except NameError:
            return False

    def run(self, allow_interactive=True):
        """Enter the native GUI event loop.

        Parameters
        ----------
        allow_interactive : bool
            Is the application allowed to handle interactive mode for console
            terminals?  By default, typing ``python -i main.py`` results in
            an interactive shell that also regularly calls the VisPy event
            loop.  In this specific case, the run() function will terminate
            immediately and rely on the interpreter's input loop to be run
            after script execution.
        """
        if os.getenv("_VISPY_RUNNING_GALLERY_EXAMPLES"):
            # Custom sphinx-gallery scraper in doc/conf.py will handle
            # rendering/running the application. To make example scripts look
            # like what a user actually has to run to view the window, we let
            # them run "app.run()" but immediately return here.
            # Without this the application would block until someone closed the
            # window that opens.
            return 0
        elif not allow_interactive or not self.is_interactive():
            return self._backend._vispy_run()

    def reuse(self):
        """Called when the application is reused in an interactive session.
        This allow the backend to do stuff in the client when `use_app()` is
        called multiple times by the user. For example, the notebook backends
        need to inject JavaScript code as soon as `use_app()` is called.
        """
        return self._backend._vispy_reuse()

    def quit(self):
        """Quit the native GUI event loop."""
        return self._backend._vispy_quit()

    @property
    def native(self):
        """The native GUI application instance."""
        return self._backend._vispy_get_native_app()

    def _use(self, backend_name=None):
        """Select a backend by name. See class docstring for details."""
        # See if we're in a specific testing mode, if so DONT check to see
        # if it's a valid backend. If it isn't, it's a good thing we
        # get an error later because we should have decorated our test
        # with requires_application()
        test_name = os.getenv('_VISPY_TESTING_APP', None)

        # Check whether the given name is valid
        if backend_name is not None:
            if backend_name.lower() == 'default':
                backend_name = None  # Explicitly use default, avoid using test
            elif backend_name.lower() not in BACKENDMAP:
                raise ValueError('backend_name must be one of %s or None, not '
                                 '%r' % (BACKEND_NAMES, backend_name))
        elif test_name is not None:
            backend_name = test_name.lower()
            assert backend_name in BACKENDMAP
        elif self.is_notebook():
            backend_name = 'jupyter_rfb'

        # Should we try and load any backend, or just this specific one?
        try_others = backend_name is None

        # Get backends to try ...
        imported_toolkits = []  # Backends for which the native lib is imported
        backends_to_try = []
        if not try_others:
            # We should never hit this, since we check above
            assert backend_name.lower() in BACKENDMAP.keys()
            # Add it
            backends_to_try.append(backend_name.lower())
        else:
            # See if a backend is loaded
            for name, module_name, native_module_name in CORE_BACKENDS:
                if native_module_name and native_module_name in sys.modules:
                    imported_toolkits.append(name.lower())
                    backends_to_try.append(name.lower())
            # See if a default is given
            default_backend = config['default_backend'].lower()
            if default_backend.lower() in BACKENDMAP.keys():
                if default_backend not in backends_to_try:
                    backends_to_try.append(default_backend)
            # After this, try each one
            for name, module_name, native_module_name in CORE_BACKENDS:
                name = name.lower()
                if name not in backends_to_try:
                    backends_to_try.append(name)

        # Now try each one
        for key in backends_to_try:
            name, module_name, native_module_name = BACKENDMAP[key]
            TRIED_BACKENDS.append(name)
            mod_name = 'backends.' + module_name
            __import__(mod_name, globals(), level=1)
            mod = getattr(backends, module_name)
            if not mod.available:
                msg = ('Could not import backend "%s":\n%s'
                       % (name, str(mod.why_not)))
                if not try_others:
                    # Fail if user wanted to use a specific backend
                    raise RuntimeError(msg)
                elif key in imported_toolkits:
                    # Warn if were unable to use an already imported toolkit
                    msg = ('Although %s is already imported, the %s backend '
                           'could not\nbe used ("%s"). \nNote that running '
                           'multiple GUI toolkits simultaneously can cause '
                           'side effects.' %
                           (native_module_name, name, str(mod.why_not)))
                    logger.warning(msg)
                elif backend_name is not None:
                    # Inform only if one isn't available
                    logger.warning(msg)
            else:
                # Success!
                self._backend_module = mod
                logger.info('Selected backend %s' % module_name)
                break
        else:
            raise RuntimeError('Could not import any of the backends. '
                               'You need to install any of %s. We recommend '
                               'PyQt' % [b[0] for b in CORE_BACKENDS])

        # Store classes for app backend and canvas backend
        self._backend = self.backend_module.ApplicationBackend()
