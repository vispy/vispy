# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""Vispy configuration functions."""

import io
import os
from os import path as op
import inspect
import json
import sys
import platform
import getopt
import traceback
import tempfile
import atexit
from shutil import rmtree

import numpy as np

from .event import EmitterGroup, EventEmitter, Event
from .logs import logger, set_log_level, use_log_level

file_types = [io.TextIOWrapper, io.BufferedRandom]
try:
    file_types += [tempfile._TemporaryFileWrapper]  # Py3k Windows this happens
except Exception:
    pass
file_types = tuple(file_types)

config = None
_data_path = None
_allowed_config_keys = None


def _init():
    """Create global Config object, parse command flags."""
    global config, _data_path, _allowed_config_keys

    app_dir = _get_vispy_app_dir()
    if app_dir is not None:
        _data_path = op.join(app_dir, 'data')
        _test_data_path = op.join(app_dir, 'test_data')
    else:
        _data_path = _test_data_path = None

    # All allowed config keys and the types they may have
    _allowed_config_keys = {
        'data_path': (str,),
        'default_backend': (str,),
        'gl_backend': (str,),
        'gl_debug': (bool,),
        'glir_file': (str,) + file_types,
        'include_path': list,
        'logging_level': (str,),
        'qt_lib': (str,),
        'dpi': (int, type(None)),
        'profile': (str, type(None),),
        'audit_tests': (bool,),
        'test_data_path': (str, type(None),),
    }

    # Default values for all config options
    default_config_options = {
        'data_path': _data_path,
        'default_backend': '',
        'gl_backend': 'gl2',
        'gl_debug': False,
        'glir_file': '',
        'include_path': [],
        'logging_level': 'warning',
        'qt_lib': 'any',
        'dpi': None,
        'profile': None,
        'audit_tests': False,
        'test_data_path': _test_data_path,
    }

    config = Config(**default_config_options)

    try:
        config.update(**_load_config())
    except Exception as err:
        raise Exception('Error while reading vispy config file "%s":\n  %s' %
                        (_get_config_fname(), str(err)))
    set_log_level(config['logging_level'])

    _parse_command_line_arguments()


###############################################################################
# Command line flag parsing

VISPY_HELP = """
VisPy command line arguments:

  --vispy-backend=(qt|pyqt5|pyqt6|pyside2|pyside6|glfw|pyglet|sdl2|wx)
    Selects the backend system for VisPy to use. This will override the default
    backend selection in your configuration file.

  --vispy-log=(debug|info|warning|error|critical)[,search string]
    Sets the verbosity of logging output. The default is 'warning'. If a search
    string is given, messages will only be displayed if they match the string,
    or if their call location (module.class:method(line) or
    module:function(line)) matches the string.

  --vispy-dpi=resolution
    Force the screen resolution to a certain value (in pixels per inch). By
    default, the OS is queried to determine the screen DPI.

  --vispy-fps
    Print the framerate (in Frames Per Second) in the console.

  --vispy-gl-debug
    Enables error checking for all OpenGL calls.

  --vispy-glir-file
    Export glir commands to specified file.

  --vispy-profile=locations
    Measure performance at specific code locations and display results.
    *locations* may be "all" or a comma-separated list of method names like
    "SceneCanvas.draw_visual".

  --vispy-cprofile
    Enable profiling using the built-in cProfile module and display results
    when the program exits.

  --vispy-audit-tests
    Enable user auditing of image test results.

  --vispy-help
    Display this help message.

"""


def _parse_command_line_arguments():
    """Transform vispy specific command line args to vispy config.
    Put into a function so that any variables dont leak in the vispy namespace.
    """
    global config
    # Get command line args for vispy
    argnames = ['vispy-backend=', 'vispy-gl-debug', 'vispy-glir-file=',
                'vispy-log=', 'vispy-help', 'vispy-profile=', 'vispy-cprofile',
                'vispy-dpi=', 'vispy-audit-tests']
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
            elif o == '--vispy-glir-file':
                config['glir_file'] = a
            elif o == '--vispy-log':
                if ',' in a:
                    verbose, match = a.split(',')
                else:
                    verbose = a
                    match = None
                config['logging_level'] = a
                set_log_level(verbose, match)
            elif o == '--vispy-profile':
                config['profile'] = a
            elif o == '--vispy-cprofile':
                _enable_profiling()
            elif o == '--vispy-help':
                print(VISPY_HELP)
            elif o == '--vispy-dpi':
                config['dpi'] = int(a)
            elif o == '--vispy-audit-tests':
                config['audit_tests'] = True
            else:
                logger.warning("Unsupported vispy flag: %s" % o)


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
    """Event indicating a configuration change.

    This class has a 'changes' attribute which is a dict of all name:value
    pairs that have changed in the configuration.
    """

    def __init__(self, changes):
        Event.__init__(self, type='config_change')
        self.changes = changes


class Config(object):
    """Container for global settings used application-wide in vispy.

    Events:

    - Config.events.changed - Emits ConfigEvent whenever the configuration changes.

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
        global _allowed_config_keys
        # check values against acceptable ones
        known_keys = _allowed_config_keys
        if key not in known_keys:
            raise KeyError('key "%s" not in known keys: "%s"'
                           % (key, known_keys))
        if not isinstance(val, known_keys[key]):
            raise TypeError('Value for key "%s" must be one of %s, not %s.'
                            % (key, known_keys[key], type(val)))

    def update(self, **kwargs):
        for key, val in kwargs.items():
            self._check_key_val(key, val)
        self._config.update(kwargs)
        self.events.changed(changes=kwargs)

    def __repr__(self):
        return repr(self._config)


def get_config_keys():
    """The config keys known by vispy and their allowed data types.

    Returns
    -------
    keys : dict
        Dict of {key: (types,)} pairs.
    """
    global _allowed_config_keys
    return _allowed_config_keys.copy()


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


def set_data_dir(directory=None, create=False, save=False):
    """Set vispy data download directory

    Parameters
    ----------
    directory : str | None
        The directory to use.
    create : bool
        If True, create directory if it doesn't exist.
    save : bool
        If True, save the configuration to the vispy config.
    """
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


def _enable_profiling():
    """Start profiling and register callback to print stats when the program
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

    out = 'Platform: %s\n' % platform.platform()
    out += 'Python:   %s\n' % str(sys.version).replace('\n', ' ')
    out += 'NumPy:    %s\n' % (np.__version__,)
    try:
        # Nest all imports here to avoid any circular imports
        from ..app import use_app, Canvas
        from ..app.backends import BACKEND_NAMES
        from ..gloo import gl
        from .check_environment import has_backend
        # get default app
        with use_log_level('warning'):
            app = use_app(call_reuse=False)  # suppress messages
        out += 'Backend:  %s\n' % app.backend_name
        for backend in BACKEND_NAMES:
            if backend.startswith('ipynb_'):
                continue
            with use_log_level('warning', print_msg=False):
                which = has_backend(backend, out=['which'])[1]
            out += '{0:<9} {1}\n'.format(backend + ':', which)
        out += '\n'
        # We need an OpenGL context to get GL info
        canvas = Canvas('Test', (10, 10), show=False, app=app)
        canvas._backend._vispy_set_current()
        out += 'GL version:  %r\n' % (gl.glGetParameter(gl.GL_VERSION),)
        x_ = gl.GL_MAX_TEXTURE_SIZE
        out += 'MAX_TEXTURE_SIZE: %r\n' % (gl.glGetParameter(x_),)
        out += 'Extensions: %r\n' % (gl.glGetParameter(gl.GL_EXTENSIONS),)
        canvas.close()
    except Exception:  # don't stop printing info
        out += 'App info-gathering error:\n%s' % traceback.format_exc()
        pass
    if fname is not None:
        with open(fname, 'w') as fid:
            fid.write(out)
    return out


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


# initialize config options
_init()


if hasattr(inspect, 'signature'):  # py35
    def _get_args(function, varargs=False):
        params = inspect.signature(function).parameters
        args = [key for key, param in params.items()
                if param.kind not in (param.VAR_POSITIONAL, param.VAR_KEYWORD)]
        if varargs:
            varargs = [param.name for param in params.values()
                       if param.kind == param.VAR_POSITIONAL]
            if len(varargs) == 0:
                varargs = None
            return args, varargs
        else:
            return args
else:
    def _get_args(function, varargs=False):
        out = inspect.getargspec(function)  # args, varargs, keywords, defaults
        if varargs:
            return out[:2]
        else:
            return out[0]
