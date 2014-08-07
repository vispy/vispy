# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

# Code inspired by original nose plugin:
# https://nose.readthedocs.org/en/latest/plugins/cover.html

from nose.plugins.base import Plugin


class MutedCoverage(Plugin):
    """Make a silent coverage report using Ned Batchelder's coverage module."""

    def configure(self, options, conf):
        Plugin.configure(self, options, conf)
        self.enabled = True
        try:
            from coverage import coverage
        except ImportError:
            self.enabled = False
            self.cov = None
            print('Module "coverage" not installed, code coverage will not '
                  'be available')
        else:
            self.enabled = True
            self.cov = coverage(auto_data=False, branch=True, data_suffix=None,
                                source=['vispy'])

    def begin(self):
        self.cov.load()
        self.cov.start()

    def report(self, stream):
        self.cov.stop()
        self.cov.combine()
        self.cov.save()
