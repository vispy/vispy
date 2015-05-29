# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import base64
import logging
import sys
import inspect
import re
import traceback
import json
from functools import partial

import numpy as np

from ..ext.six import string_types


###############################################################################
# LOGGING (some adapted from mne-python)

def _get_vispy_caller():
    """Helper to get vispy calling function from the stack"""
    records = inspect.stack()
    # first few records are vispy-based logging calls
    for record in records[5:]:
        module = record[0].f_globals['__name__']
        if module.startswith('vispy'):
            line = str(record[0].f_lineno)
            func = record[3]
            cls = record[0].f_locals.get('self', None)
            clsname = "" if cls is None else cls.__class__.__name__ + '.'
            caller = "{0}:{1}{2}({3}): ".format(module, clsname, func, line)
            return caller
    return 'unknown'


# class _WrapStdOut(object):
#     """Class to work around how doctest captures stdout"""
#     def __getattr__(self, name):
#         # Even more ridiculous than this class, this must be sys.stdout (not
#         # just stdout) in order for this to work (tested on OSX and Linux)
#         return getattr(sys.stdout, name)


class _VispyFormatter(logging.Formatter):
    """Formatter that optionally prepends caller"""
    def __init__(self):
        logging.Formatter.__init__(self, '%(levelname)s: %(message)s')
        self._vispy_prepend_caller = False

    def _vispy_set_prepend(self, prepend):
        self._vispy_prepend_caller = prepend

    def format(self, record):
        out = logging.Formatter.format(self, record)
        if self._vispy_prepend_caller:
            out = _get_vispy_caller() + out
        return out


class _VispyStreamHandler(logging.StreamHandler):
    """Stream handler allowing matching and recording

    This handler has two useful optional additions:

        1. Recording emitted messages.
        2. Performing regexp substring matching.

    Prepending of traceback information is done in _VispyFormatter.
    """
    def __init__(self):
        logging.StreamHandler.__init__(self, sys.stderr)
        self._vispy_formatter = _lf
        self.setFormatter(self._vispy_formatter)
        self._vispy_match = None
        self._vispy_emit_list = list()
        self._vispy_set_emit_record(False)
        self._vispy_set_match(None)
        self._vispy_print_msg = True

    def _vispy_emit_match_andor_record(self, record):
        """Log message emitter that optionally matches and/or records"""
        test = record.getMessage()
        match = self._vispy_match
        if (match is None or re.search(match, test) or
                re.search(match, _get_vispy_caller())):
            if self._vispy_emit_record:
                fmt_rec = self._vispy_formatter.format(record)
                self._vispy_emit_list.append(fmt_rec)
            if self._vispy_print_msg:
                return logging.StreamHandler.emit(self, record)
            else:
                return

    def _vispy_set_match(self, match):
        old_match = self._vispy_match
        self._vispy_match = match
        # Triage here to avoid a bunch of if's later (more efficient)
        if match is not None or self._vispy_emit_record:
            self.emit = self._vispy_emit_match_andor_record
        else:
            self.emit = partial(logging.StreamHandler.emit, self)
        return old_match

    def _vispy_set_emit_record(self, record):
        self._vispy_emit_record = record
        match = self._vispy_match
        # Triage here to avoid a bunch of if's later (more efficient)
        if match is not None or self._vispy_emit_record:
            self.emit = self._vispy_emit_match_andor_record
        else:
            self.emit = partial(logging.StreamHandler.emit, self)

    def _vispy_reset_list(self):
        self._vispy_emit_list = list()


logger = logging.getLogger('vispy')
_lf = _VispyFormatter()
_lh = _VispyStreamHandler()  # needs _lf to exist
logger.addHandler(_lh)

logging_types = dict(debug=logging.DEBUG, info=logging.INFO,
                     warning=logging.WARNING, error=logging.ERROR,
                     critical=logging.CRITICAL)


def set_log_level(verbose, match=None, return_old=False):
    """Convenience function for setting the logging level

    Parameters
    ----------
    verbose : bool, str, int, or None
        The verbosity of messages to print. If a str, it can be either DEBUG,
        INFO, WARNING, ERROR, or CRITICAL. Note that these are for
        convenience and are equivalent to passing in logging.DEBUG, etc.
        For bool, True is the same as 'INFO', False is the same as 'WARNING'.
    match : str | None
        String to match. Only those messages that both contain a substring
        that regexp matches ``'match'`` (and the ``verbose`` level) will be
        displayed.
    return_old : bool
        If True, return the old verbosity level and old match.

    Notes
    -----
    If ``verbose=='debug'``, then the ``vispy`` method emitting the log
    message will be prepended to each log message, which is useful for
    debugging. If ``verbose=='debug'`` or ``match is not None``, then a
    small performance overhead is added. Thus it is suggested to only use
    these options when performance is not crucial.

    See also
    --------
    vispy.util.use_log_level
    """
    # This method is responsible for setting properties of the handler and
    # formatter such that proper messages (possibly with the vispy caller
    # prepended) are displayed. Storing log messages is only available
    # via the context handler (use_log_level), so that configuration is
    # done by the context handler itself.
    if isinstance(verbose, bool):
        verbose = 'info' if verbose else 'warning'
    if isinstance(verbose, string_types):
        verbose = verbose.lower()
        if verbose not in logging_types:
            raise ValueError('Invalid argument "%s"' % verbose)
        verbose = logging_types[verbose]
    else:
        raise TypeError('verbose must be a bool or string')
    logger = logging.getLogger('vispy')
    old_verbose = logger.level
    old_match = _lh._vispy_set_match(match)
    logger.setLevel(verbose)
    if verbose <= logging.DEBUG:
        _lf._vispy_set_prepend(True)
    else:
        _lf._vispy_set_prepend(False)
    out = None
    if return_old:
        out = (old_verbose, old_match)
    return out


class use_log_level(object):
    """Context manager that temporarily sets logging level

    Parameters
    ----------
    level : str
        See ``set_log_level`` for options.
    match : str | None
        The string to match.
    record : bool
        If True, the context manager will keep a record of the logging
        messages generated by vispy. Otherwise, an empty list will
        be returned.
    print_msg : bool
        If False, printing of (all) messages will be suppressed. This is
        mainly useful in testing. False only works in `record=True` mode, if
        not recording messages, consider setting `level` appropriately.

    Returns
    -------
    records : list
        As a context manager, an empty list or the list of logging messages
        will be returned (depending on the input ``record``).
    """
    # This method mostly wraps to set_log_level, but also takes
    # care of enabling/disabling message recording in the formatter.
    def __init__(self, level, match=None, record=False, print_msg=True):
        self._new_level = level
        self._new_match = match
        self._print_msg = print_msg
        self._record = record
        if match is not None and not isinstance(match, string_types):
            raise TypeError('match must be None or str')

    def __enter__(self):
        # set the log level
        old_level, old_match = set_log_level(self._new_level,
                                             self._new_match, return_old=True)
        for key, value in logging_types.items():
            if value == old_level:
                old_level = key
        self._old_level = old_level
        self._old_match = old_match
        if not self._print_msg:
            _lh._vispy_print_msg = False
        # set handler to record, if appropriate
        _lh._vispy_reset_list()
        if self._record:
            _lh._vispy_set_emit_record(True)
            return _lh._vispy_emit_list
        else:
            return list()

    def __exit__(self, type, value, traceback):
        # reset log level
        set_log_level(self._old_level, self._old_match)
        # reset handler
        if self._record:
            _lh._vispy_set_emit_record(False)
        if not self._print_msg:
            _lh._vispy_print_msg = True  # set it back


def log_exception(level='warning', tb_skip=2):
    """
    Send an exception and traceback to the logger.
    
    This function is used in cases where an exception is handled safely but
    nevertheless should generate a descriptive error message. An extra line
    is inserted into the stack trace indicating where the exception was caught.
    
    Parameters
    ----------
    level : str
        See ``set_log_level`` for options.
    tb_skip : int
        The number of traceback entries to ignore, prior to the point where
        the exception was caught. The default is 2.
    """
    stack = "".join(traceback.format_stack()[:-tb_skip])
    tb = traceback.format_exception(*sys.exc_info())
    msg = tb[0]  # "Traceback (most recent call last):"
    msg += stack
    msg += "  << caught exception here: >>\n"
    msg += "".join(tb[1:]).rstrip()
    logger.log(logging_types[level], msg)

logger.log_exception = log_exception  # make this easier to reach


def _handle_exception(ignore_callback_errors, print_callback_errors, obj,
                      cb_event=None, node=None):
    """Helper for prining errors in callbacks

    See EventEmitter._invoke_callback for a use example.
    """
    if not hasattr(obj, '_vispy_err_registry'):
        obj._vispy_err_registry = {}
    registry = obj._vispy_err_registry

    if cb_event is not None:
        cb, event = cb_event
        exp_type = 'callback'
    else:
        exp_type = 'node'
    type_, value, tb = sys.exc_info()
    tb = tb.tb_next  # Skip *this* frame
    sys.last_type = type_
    sys.last_value = value
    sys.last_traceback = tb
    del tb  # Get rid of it in this namespace
    # Handle
    if not ignore_callback_errors:
        raise
    if print_callback_errors != "never":
        this_print = 'full'
        if print_callback_errors in ('first', 'reminders'):
            # need to check to see if we've hit this yet
            if exp_type == 'callback':
                key = repr(cb) + repr(event)
            else:
                key = repr(node)
            if key in registry:
                registry[key] += 1
                if print_callback_errors == 'first':
                    this_print = None
                else:  # reminders
                    ii = registry[key]
                    # Use logarithmic selection
                    # (1, 2, ..., 10, 20, ..., 100, 200, ...)
                    if ii == (2 ** int(np.log2(ii))):
                        this_print = ii
                    else:
                        this_print = None
            else:
                registry[key] = 1
        if this_print == 'full':
            logger.log_exception()
            if exp_type == 'callback':
                logger.error("Invoking %s for %s" % (cb, event))
            else:  # == 'node':
                logger.error("Drawing node %s" % node)
        elif this_print is not None:
            if exp_type == 'callback':
                logger.error("Invoking %s repeat %s"
                             % (cb, this_print))
            else:  # == 'node':
                logger.error("Drawing node %s repeat %s"
                             % (node, this_print))


def _serialize_buffer(buffer, array_serialization=None):
    """Serialize a NumPy array."""
    if array_serialization == 'binary':
        # WARNING: in NumPy 1.9, tostring() has been renamed to tobytes()
        # but tostring() is still here for now for backward compatibility.
        return buffer.ravel().tostring()
    elif array_serialization == 'base64':
        return {'storage_type': 'base64',
                'buffer': base64.b64encode(buffer).decode('ascii')
                }
    raise ValueError("The array serialization method should be 'binary' or "
                     "'base64'.")


class NumPyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return _serialize_buffer(obj, array_serialization='base64')
        elif isinstance(obj, np.generic):
            return obj.item()

        return json.JSONEncoder.default(self, obj)
