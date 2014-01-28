# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import logging
import sys

from .six import string_types

###############################################################################
# LOGGING (some adapted from mne-python)


class _WrapStdOut(object):
    """Class to work around how doctest captures stdout"""
    def __getattr__(self, name):
        # Even more ridiculous than this class, this must be sys.stdout (not
        # just stdout) in order for this to work (tested on OSX and Linux)
        return getattr(sys.stdout, name)


logger = logging.getLogger('vispy')
_output_format = '%(message)s'
_lh = logging.StreamHandler(_WrapStdOut())
_lh.setFormatter(logging.Formatter(_output_format))
logger.addHandler(_lh)


logging_types = dict(debug=logging.DEBUG, info=logging.INFO,
                     warning=logging.WARNING, error=logging.ERROR,
                     critical=logging.CRITICAL)

def set_log_level(verbose, return_old_level=False):
    """Convenience function for setting the logging level

    Parameters
    ----------
    verbose : bool, str, int, or None
        The verbosity of messages to print. If a str, it can be either DEBUG,
        INFO, WARNING, ERROR, or CRITICAL. Note that these are for
        convenience and are equivalent to passing in logging.DEBUG, etc.
        For bool, True is the same as 'INFO', False is the same as 'WARNING'.
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
    logger.setLevel(verbose)
    return (old_verbose if return_old_level else None)


class use_log_level(object):
    """Context manager that temporarily sets logging level

    Parameters
    ----------
    level : str
        See ``set_log_level`` for options
    """
    def __init__(self, level):
        self._new_level = level

    def __enter__(self):
        old_level = set_log_level(self._new_level, return_old_level=True)
        for key, value in logging_types.items():
            if value == old_level:
                old_level = key
        self._old_level = old_level
        return self

    def __exit__(self, type, value, traceback):
        set_log_level(self._old_level)
