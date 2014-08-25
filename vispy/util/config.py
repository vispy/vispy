# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""Vispy configuration functions
"""

import os
from os import path as op
import json
import sys
import platform
import getopt
import traceback
import tempfile
import atexit
from shutil import rmtree

from .event import EmitterGroup, EventEmitter, Event
from ..ext.six import string_types
from .logs import logger, set_log_level, use_log_level


class _TempDir(str):
    """Class for creating and auto-destroying temp dir

    This is designed to be used with testing modules.

    We cannot simply use __del__() method for cleanup here because the rmtree
    function may be cleaned up before this object, so we use the atexit module
    instead.
    """
    def __new__(self):
        new = str.__new__(self, tempfile.mkdtemp())
        return new

    def __init__(self):
        self._path = self.__str__()
        atexit.register(self.cleanup)

    def cleanup(self):
        rmtree(self._path, ignore_errors=True)


###############################################################################
# CONFIG

# Adapted from pyzolib/paths.py:
# https://bitbucket.org/pyzo/pyzolib/src/tip/paths.py
def _get_vispy_app_dir():
    """Helper to get the default directory for storing vispy data"""
    # Define default user directory
    user_dir = os.path.expanduser('~')

    # Get system app data dir
    path = None
    if sys.platform.startswith('win'):
        path1, path2 = os.getenv('LOCALAPPDATA'), os.getenv('APPDATA')
        path = path1 or path2
    elif sys.platform.startswith('darwin'):
        path = os.path.join(user_dir, 'Library', 'Application Support')
    # On Linux and as fallback
    if not (path and os.path.isdir(path)):
        path = user_dir

    # Maybe we should store things local to the executable (in case of a
    # portable distro or a frozen application that wants to be portable)
    prefix = sys.prefix
    if getattr(sys, 'frozen', None):  # See application_dir() function
        prefix = os.path.abspath(os.path.dirname(sys.path[0]))
    for reldir in ('settings', '../settings'):
        localpath = os.path.abspath(os.path.join(prefix, reldir))
        if os.path.isdir(localpath):
            try:
                open(os.path.join(localpath, 'test.write'), 'wb').close()
                os.remove(os.path.join(localpath, 'test.write'))
            except IOError:
                pass  # We cannot write in this directory
            else:
                path = localpath
                break

    # Get path specific for this app
    appname = '.vispy' if path == user_dir else 'vispy'
    path = os.path.join(path, appname)
    return path


class ConfigEvent(Event):

    """ Event indicating a configuration change.

    This class has a 'changes' attribute which is a dict of all name:value
    pairs that have changed in the configuration.
    """

    def __init__(self, changes):
        Event.__init__(self, type='config_change')
        self.changes = changes


class Config(object):

    """ Container for global settings used application-wide in vispy.

    Events:
    -------
    Config.events.changed - Emits ConfigEvent whenever the configuration
    changes.
    """

    def __init__(self, **kwargs):
        self.events = EmitterGroup(source=self)
        self.events['changed'] = EventEmitter(
            event_class=ConfigEvent,
            source=self)
        self._config = {}
        self.update(**kwargs)
        self._known_keys = get_config_keys()

    def __getitem__(self, item):
        return self._config[item]

    def __setitem__(self, item, val):
        self._check_key_val(item, val)
        self._config[item] = val
        # inform any listeners that a configuration option has changed
        self.events.changed(changes={item: val})

    def _check_key_val(self, key, val):
        # check values against acceptable ones
        known_keys = get_config_keys()
        if key not in known_keys:
            raise KeyError('key "%s" not in known keys: "%s"'
                           % (key, known_keys))
        if not isinstance(val, (string_types, bool)):
            raise TypeError('Value for key "%s" must be str or bool, not %s'
                            % (key, type(val)))

    def update(self, **kwargs):
        for key, val in kwargs.items():
            self._check_key_val(key, val)
        self._config.update(kwargs)
        self.events.changed(changes=kwargs)

    def __repr__(self):
        return repr(self._config)


def get_config_keys():
    """The config keys known by vispy

    Returns
    -------
    keys : tuple
        List of known config keys.
    """
    return ('data_path', 'default_backend', 'gl_debug', 'logging_level',
            'qt_lib')


def _get_config_fname():
    """Helper for the vispy config file"""
    directory = _get_vispy_app_dir()
    if directory is None:
        return None
    fname = op.join(directory, 'vispy.json')
    if os.environ.get('_VISPY_CONFIG_TESTING', None) is not None:
        fname = op.join(_TempDir(), 'vispy.json')
    return fname


def _load_config():
    """Helper to load prefs from ~/.vispy/vispy.json"""
    fname = _get_config_fname()
    if fname is None or not op.isfile(fname):
        return dict()
    with open(fname, 'r') as fid:
        config = json.load(fid)
    return config


def save_config(**kwargs):
    """Save configuration keys to vispy config file

    Parameters
    ----------
    **kwargs : keyword arguments
        Key/value pairs to save to the config file.
    """
    if kwargs == {}:
        kwargs = config._config
    current_config = _load_config()
    current_config.update(**kwargs)
    # write to disk
    fname = _get_config_fname()
    if fname is None:
        raise RuntimeError('config filename could not be determined')
    if not op.isdir(op.dirname(fname)):
        os.mkdir(op.dirname(fname))
    with open(fname, 'w') as fid:
        json.dump(current_config, fid, sort_keys=True, indent=0)


_data_path = _get_vispy_app_dir()
if _data_path is not None:
    _data_path = op.join(_data_path, 'data')
config = Config(default_backend='qt', qt_lib='any',
                gl_debug=False, logging_level='info',
                data_path=_data_path)
try:
    config.update(**_load_config())
except Exception as err:
    raise Exception('Error while reading vispy config file "%s":\n  %s' %
                    (_get_config_fname(), err.message))
set_log_level(config['logging_level'])


def set_data_dir(directory=None, create=False, save=False):
    """Set vispy data download directory"""
    if directory is None:
        directory = _data_path
        if _data_path is None:
            raise IOError('default path cannot be determined, please '
                          'set it manually (directory != None)')
    if not op.isdir(directory):
        if not create:
            raise IOError('directory "%s" does not exist, perhaps try '
                          'create=True to create it?' % directory)
        os.mkdir(directory)
    config.update(data_path=directory)
    if save:
        save_config(data_path=directory)


###############################################################################
# System information and parsing

VISPY_HELP = """
VisPy command line arguments:

  --vispy-backend=(qt|pyqt|pyside|glut|glfw|pyglet)
    Selects the backend system for VisPy to use. This will override the default
    backend selection in your configuration file.
    
  --vispy-log=(debug|info|warning|error|critical)[,search string]
    Sets the verbosity of logging output. The default is 'warning'. If a search
    string is given, messages will only be displayed if they match the string,
    or if their call location (module.class:method(line) or 
    module:function(line)) matches the string.    
    
  --vispy-fps
    Print the framerate (in Frames Per Second) in the console.
    
  --vispy-gl-debug
    Enables error checking for all OpenGL calls.

  --vispy-profile
    Enable profiling and print the results when the program exits.
    
  --vispy-help
    Display this help message.

"""


def _parse_command_line_arguments():
    """ Transform vispy specific command line args to vispy config.
    Put into a function so that any variables dont leak in the vispy namespace.
    """
    # Get command line args for vispy
    argnames = ['vispy-backend=', 'vispy-gl-debug', 'vispy-log=', 'vispy-help',
                'vispy-profile']
    try:
        opts, args = getopt.getopt(sys.argv[1:], '', argnames)
    except getopt.GetoptError:
        opts = []
    # Use them to set the config values
    for o, a in opts:
        if o.startswith('--vispy'):
            if o == '--vispy-backend':
                config['default_backend'] = a
                logger.info('vispy backend: %s', a)
            elif o == '--vispy-gl-debug':
                config['gl_debug'] = True
            elif o == '--vispy-log':
                if ',' in a:
                    verbose, match = a.split(',')
                else:
                    verbose = a
                    match = None
                config['logging_level'] = a
                set_log_level(verbose, match)
            elif o == '--vispy-profile':
                _enable_profiling()
            elif o == '--vispy-help':
                print(VISPY_HELP)
            else:
                logger.warning("Unsupported vispy flag: %s" % o)


def _enable_profiling():
    """ Start profiling and register callback to print stats when the program
    exits.
    """
    import cProfile
    import atexit
    global _profiler
    _profiler = cProfile.Profile()
    _profiler.enable()
    atexit.register(_profile_atexit)


_profiler = None


def _profile_atexit():
    global _profiler
    _profiler.print_stats(sort='cumulative')


def sys_info(fname=None, overwrite=False):
    """Get relevant system and debugging information

    Parameters
    ----------
    fname : str | None
        Filename to dump info to. Use None to simply print.
    overwrite : bool
        If True, overwrite file (if it exists).

    Returns
    -------
    out : str
        The system information as a string.
    """
    if fname is not None and op.isfile(fname) and not overwrite:
        raise IOError('file exists, use overwrite=True to overwrite')

    out = ''
    try:
        # Nest all imports here to avoid any circular imports
        from ..app import use_app, Canvas
        from ..app.backends import BACKEND_NAMES
        from ..gloo import gl
        from ..testing import has_backend
        # get default app
        with use_log_level('warning'):
            app = use_app()  # suppress messages
        out += 'Platform: %s\n' % platform.platform()
        out += 'Python:   %s\n' % str(sys.version).replace('\n', ' ')
        out += 'Backend:  %s\n' % app.backend_name
        for backend in BACKEND_NAMES:
            with use_log_level('warning', print_msg=False):
                which = has_backend(backend, out=['which'])[1]
            out += '{0:<9} {1}\n'.format(backend + ':', which)
        out += '\n'
        # We need an OpenGL context to get GL info
        if 'glut' in app.backend_name.lower():
            # glut causes problems
            out += 'OpenGL information omitted for glut backend\n'
        else:
            canvas = Canvas('Test', (10, 10), show=False, app=app)
            canvas._backend._vispy_set_current()
            out += 'GL version:  %s\n' % gl.glGetParameter(gl.GL_VERSION)
            x_ = gl.GL_MAX_TEXTURE_SIZE
            out += 'MAX_TEXTURE_SIZE: %d\n' % gl.glGetParameter(x_)
            out += 'Extensions: %s\n' % gl.glGetParameter(gl.GL_EXTENSIONS)
            canvas.close()
    except Exception:  # don't stop printing info
        out += '\nInfo-gathering error:\n%s' % traceback.format_exc()
        pass
    if fname is not None:
        with open(fname, 'w') as fid:
            fid.write(out)
    return out
