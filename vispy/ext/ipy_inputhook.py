# coding: utf-8
"""
Inputhook management for GUI event loop integration.
"""

#-----------------------------------------------------------------------------
# Source:
#   https://github.com/ipython/ipython/commits/master/IPython/lib/inputhook.py
# Revision:
#   29a0deb452d4fa7f59edb7e059c1a46ceb5a124d
# Modifications:
#   Removed dependencies and other backends for VisPy.
#-----------------------------------------------------------------------------
#  Copyright (C) 2008-2011  The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

try:
    import ctypes
except ImportError:
    ctypes = None
except SystemError: # IronPython issue, 2/8/2014
    ctypes = None
import os
import sys

from distutils.version import LooseVersion as V


#-----------------------------------------------------------------------------
# Constants
#-----------------------------------------------------------------------------

# Constants for identifying the GUI toolkits.
GUI_WX = 'wx'
GUI_QT = 'qt'
GUI_QT4 = 'qt4'
GUI_GTK = 'gtk'
GUI_TK = 'tk'
GUI_OSX = 'osx'
GUI_PYGLET = 'pyglet'
GUI_GTK3 = 'gtk3'
GUI_NONE = 'none' # i.e. disable

#-----------------------------------------------------------------------------
# Utilities
#-----------------------------------------------------------------------------

def _stdin_ready_posix():
    """Return True if there's something to read on stdin (posix version)."""
    infds, outfds, erfds = select.select([sys.stdin],[],[],0)
    return bool(infds)

def _stdin_ready_nt():
    """Return True if there's something to read on stdin (nt version)."""
    return msvcrt.kbhit()

def _stdin_ready_other():
    """Return True, assuming there's something to read on stdin."""
    return True #


def _ignore_CTRL_C_posix():
    """Ignore CTRL+C (SIGINT)."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def _allow_CTRL_C_posix():
    """Take CTRL+C into account (SIGINT)."""
    signal.signal(signal.SIGINT, signal.default_int_handler)

def _ignore_CTRL_C_other():
    """Ignore CTRL+C (not implemented)."""
    pass

def _allow_CTRL_C_other():
    """Take CTRL+C into account (not implemented)."""
    pass

if os.name == 'posix':
    import select
    import signal
    stdin_ready = _stdin_ready_posix
    ignore_CTRL_C = _ignore_CTRL_C_posix
    allow_CTRL_C = _allow_CTRL_C_posix
elif os.name == 'nt':
    import msvcrt
    stdin_ready = _stdin_ready_nt
    ignore_CTRL_C = _ignore_CTRL_C_other
    allow_CTRL_C = _allow_CTRL_C_other
else:
    stdin_ready = _stdin_ready_other
    ignore_CTRL_C = _ignore_CTRL_C_other
    allow_CTRL_C = _allow_CTRL_C_other


#-----------------------------------------------------------------------------
# Main InputHookManager class
#-----------------------------------------------------------------------------


class InputHookManager(object):
    """Manage PyOS_InputHook for different GUI toolkits.

    This class installs various hooks under ``PyOSInputHook`` to handle
    GUI event loop integration.
    """
    
    def __init__(self):
        if ctypes is None:
            print("IPython GUI event loop requires ctypes, %gui will not be available")
            return
        self.PYFUNC = ctypes.PYFUNCTYPE(ctypes.c_int)
        self.guihooks = {}
        self.aliases = {}
        self.apps = {}
        self._reset()

    def _reset(self):
        self._callback_pyfunctype = None
        self._callback = None
        self._installed = False
        self._current_gui = None

    def get_pyos_inputhook(self):
        """Return the current PyOS_InputHook as a ctypes.c_void_p."""
        return ctypes.c_void_p.in_dll(ctypes.pythonapi,"PyOS_InputHook")

    def get_pyos_inputhook_as_func(self):
        """Return the current PyOS_InputHook as a ctypes.PYFUNCYPE."""
        return self.PYFUNC.in_dll(ctypes.pythonapi,"PyOS_InputHook")

    def set_inputhook(self, callback):
        """Set PyOS_InputHook to callback and return the previous one."""
        # On platforms with 'readline' support, it's all too likely to
        # have a KeyboardInterrupt signal delivered *even before* an
        # initial ``try:`` clause in the callback can be executed, so
        # we need to disable CTRL+C in this situation.
        ignore_CTRL_C()
        self._callback = callback
        self._callback_pyfunctype = self.PYFUNC(callback)
        pyos_inputhook_ptr = self.get_pyos_inputhook()
        original = self.get_pyos_inputhook_as_func()
        pyos_inputhook_ptr.value = \
            ctypes.cast(self._callback_pyfunctype, ctypes.c_void_p).value
        self._installed = True
        return original

    def clear_inputhook(self, app=None):
        """Set PyOS_InputHook to NULL and return the previous one.

        Parameters
        ----------
        app : optional, ignored
          This parameter is allowed only so that clear_inputhook() can be
          called with a similar interface as all the ``enable_*`` methods.  But
          the actual value of the parameter is ignored.  This uniform interface
          makes it easier to have user-level entry points in the main IPython
          app like :meth:`enable_gui`."""
        pyos_inputhook_ptr = self.get_pyos_inputhook()
        original = self.get_pyos_inputhook_as_func()
        pyos_inputhook_ptr.value = ctypes.c_void_p(None).value
        allow_CTRL_C()
        self._reset()
        return original

    def clear_app_refs(self, gui=None):
        """Clear IPython's internal reference to an application instance.

        Whenever we create an app for a user on qt4 or wx, we hold a
        reference to the app.  This is needed because in some cases bad things
        can happen if a user doesn't hold a reference themselves.  This
        method is provided to clear the references we are holding.

        Parameters
        ----------
        gui : None or str
            If None, clear all app references.  If ('wx', 'qt4') clear
            the app for that toolkit.  References are not held for gtk or tk
            as those toolkits don't have the notion of an app.
        """
        if gui is None:
            self.apps = {}
        elif gui in self.apps:
            del self.apps[gui]

    def register(self, toolkitname, *aliases):
        """Register a class to provide the event loop for a given GUI.
        
        This is intended to be used as a class decorator. It should be passed
        the names with which to register this GUI integration. The classes
        themselves should subclass :class:`InputHookBase`.
        
        ::
        
            @inputhook_manager.register('qt')
            class QtInputHook(InputHookBase):
                def enable(self, app=None):
                    ...
        """
        def decorator(cls):
            inst = cls(self)
            self.guihooks[toolkitname] = inst
            for a in aliases:
                self.aliases[a] = toolkitname
            return cls
        return decorator

    def current_gui(self):
        """Return a string indicating the currently active GUI or None."""
        return self._current_gui

    def enable_gui(self, gui=None, app=None):
        """Switch amongst GUI input hooks by name.

        This is a higher level method than :meth:`set_inputhook` - it uses the
        GUI name to look up a registered object which enables the input hook
        for that GUI.

        Parameters
        ----------
        gui : optional, string or None
          If None (or 'none'), clears input hook, otherwise it must be one
          of the recognized GUI names (see ``GUI_*`` constants in module).

        app : optional, existing application object.
          For toolkits that have the concept of a global app, you can supply an
          existing one.  If not given, the toolkit will be probed for one, and if
          none is found, a new one will be created.  Note that GTK does not have
          this concept, and passing an app if ``gui=="GTK"`` will raise an error.

        Returns
        -------
        The output of the underlying gui switch routine, typically the actual
        PyOS_InputHook wrapper object or the GUI toolkit app created, if there was
        one.
        """
        if gui in (None, GUI_NONE):
            return self.disable_gui()
        
        if gui in self.aliases:
            return self.enable_gui(self.aliases[gui], app)
        
        try:
            gui_hook = self.guihooks[gui]
        except KeyError:
            e = "Invalid GUI request {!r}, valid ones are: {}"
            raise ValueError(e.format(gui, ', '.join(self.guihooks)))
        self._current_gui = gui

        app = gui_hook.enable(app)
        if app is not None:
            app._in_event_loop = True
            self.apps[gui] = app        
        return app

    def disable_gui(self):
        """Disable GUI event loop integration.
        
        If an application was registered, this sets its ``_in_event_loop``
        attribute to False. It then calls :meth:`clear_inputhook`.
        """
        gui = self._current_gui
        if gui in self.apps:
            self.apps[gui]._in_event_loop = False
        return self.clear_inputhook()

class InputHookBase(object):
    """Base class for input hooks for specific toolkits.
    
    Subclasses should define an :meth:`enable` method with one argument, ``app``,
    which will either be an instance of the toolkit's application class, or None.
    They may also define a :meth:`disable` method with no arguments.
    """
    def __init__(self, manager):
        self.manager = manager

    def disable(self):
        pass

inputhook_manager = InputHookManager()

@inputhook_manager.register('osx')
class NullInputHook(InputHookBase):
    """A null inputhook that doesn't need to do anything"""
    def enable(self, app=None):
        pass

clear_inputhook = inputhook_manager.clear_inputhook
set_inputhook = inputhook_manager.set_inputhook
current_gui = inputhook_manager.current_gui
clear_app_refs = inputhook_manager.clear_app_refs
enable_gui = inputhook_manager.enable_gui
disable_gui = inputhook_manager.disable_gui
register = inputhook_manager.register
guis = inputhook_manager.guihooks