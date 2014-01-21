# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""Miscellaneous functions
"""

import tempfile
import atexit
from shutil import rmtree

from .six import string_types


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


def is_string(s):
    return isinstance(s, string_types)
