# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
from gzip import GzipFile


# Python < 2.7 doesn't have context handling
class gzip_open(GzipFile):
    def __enter__(self):
        if hasattr(GzipFile, '__enter__'):
            return GzipFile.__enter__(self)
        else:
            return self

    def __exit__(self, exc_type, exc_value, traceback):
        if hasattr(GzipFile, '__exit__'):
            return GzipFile.__exit__(self, exc_type, exc_value, traceback)
        else:
            return self.close()
