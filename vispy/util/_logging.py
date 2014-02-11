# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import logging
import sys
import inspect
import re

from .six import string_types


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
            caller = "{0}:{1}({2}): ".format(module, func, line)
            return caller
    return 'unknown'


class _WrapStdOut(object):
    """Class to work around how doctest captures stdout"""
    def __getattr__(self, name):
        # Even more ridiculous than this class, this must be sys.stdout (not
        # just stdout) in order for this to work (tested on OSX and Linux)
        return getattr(sys.stdout, name)


class _VispyFormatter(logging.Formatter):
    """Formatter that prepends caller in debug mode"""
    def __init__(self):
        logging.Formatter.__init__(self, '%(levelname)s: %(message)s')

    def format(self, record):
        out = logging.Formatter.format(self, record)
        if logger.level <= logging.DEBUG:
            out = _get_vispy_caller() + out
        return out


class _VispyStreamHandler(logging.StreamHandler):
    """Stream handler allowing matching and recording"""
    def __init__(self):
        logging.StreamHandler.__init__(self, _WrapStdOut())
        self._vispy_formatter = _VispyFormatter()
        self.setFormatter(self._vispy_formatter)
        self._vispy_match = None
        self._vispy_emit_list = list()
        self._vispy_set_emit_record(False)
        self._vispy_set_match(None)

    def _vispy_emit_match(self, record):
        test = record.getMessage()
        match = self._vispy_match
        if match is None or len(re.findall(match, test)) > 0:
            if self._vispy_emit_record:
                fmt_rec = self._vispy_formatter.format(record)
                self._vispy_emit_list.append(fmt_rec)
            return logging.StreamHandler.emit(self, record)

    def _vispy_emit(self, record):
        return logging.StreamHandler.emit(self, record)

    def _vispy_set_match(self, match):
        old_match = self._vispy_match
        self._vispy_match = match
        # Triage here to avoid a bunch of if's later (more efficient)
        if match is not None or self._vispy_emit_record:
            self.emit = self._vispy_emit_match
        else:
            self.emit = self._vispy_emit
        return old_match

    def _vispy_set_emit_record(self, record):
        self._vispy_emit_record = record
        match = self._vispy_match
        # Triage here to avoid a bunch of if's later (more efficient)
        if match is not None or self._vispy_emit_record:
            self.emit = self._vispy_emit_match
        else:
            self.emit = self._vispy_emit

    def _vispy_reset_list(self):
        self._vispy_emit_list = list()


logger = logging.getLogger('vispy')
_lh = _VispyStreamHandler()
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
    return_old_level : bool
        If True, return the old verbosity level.
    """
    if isinstance(verbose, bool):
        verbose = 'info' if verbose else 'warning'
    if isinstance(verbose, string_types):
        verbose = verbose.lower()
        if not verbose in logging_types:
            raise ValueError('verbose must be of a valid type')
        verbose = logging_types[verbose]
    else:
        raise TypeError('verbose must be a bool or string')
    logger = logging.getLogger('vispy')
    old_verbose = logger.level
    old_match = _lh._vispy_set_match(match)
    logger.setLevel(verbose)
    out = None
    if return_old:
        out = (old_verbose, old_match)
    return out


class use_log_level(object):
    """Context manager that temporarily sets logging level

    Parameters
    ----------
    level : str
        See ``set_log_level`` for options
    """
    def __init__(self, level, match=None, record=False):
        self._new_level = level
        self._new_match = match
        self._record = record
        if match is not None and not isinstance(match, string_types):
            raise TypeError('match must be None or str')

    def __enter__(self):
        old_level, old_match = set_log_level(self._new_level,
                                             self._new_match, return_old=True)
        for key, value in logging_types.items():
            if value == old_level:
                old_level = key
        self._old_level = old_level
        self._old_match = old_match
        _lh._vispy_reset_list()
        if self._record:
            _lh._vispy_set_emit_record(True)
            return _lh._vispy_emit_list
        else:
            return list()

    def __exit__(self, type, value, traceback):
        set_log_level(self._old_level, self._old_match)
        if self._record:
            _lh._vispy_set_emit_record(False)
