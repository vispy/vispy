#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for mo

"""
Convenience tools for vispy developers

    make.py command [arg]

"""

from __future__ import division, print_function

import sys
import os
from os import path as op
import webbrowser
import traceback


class Maker:
    """Collection of make commands.

    To create a new command, create a method with a short name, give it
    a docstring, and make it do something useful :)

    """

    def __init__(self, argv):
        """ Parse command line arguments. """
        # Get function to call
        if len(argv) == 1:
            func, arg = self.help, ''
        else:
            command = argv[1].strip()
            arg = ' '.join(argv[2:]).strip()
            func = getattr(self, command, None)
        # Call it if we can
        if func is not None:
            func(arg)
        else:
            sys.exit('Invalid command: "%s"' % command)

    def coverage_html(self, arg):
        """Generate html report from .coverage and launch"""
        print('Generating HTML...')
        from coverage import coverage
        cov = coverage(auto_data=False, branch=True, data_suffix=None,
                       source=['vispy'])  # should match testing/_coverage.py
        cov.combine()
        cov.load()
        cov.html_report()
        print('Done, launching browser.')
        fname = op.join(os.getcwd(), 'htmlcov', 'index.html')
        if not op.isfile(fname):
            raise IOError('Generated file not found: %s' % fname)
        webbrowser.open_new_tab(fname)

    def help(self, arg):
        """ Show help message. Use 'help X' to get more help on command X. """
        if arg:
            command = arg
            func = getattr(self, command, None)
            if func is not None:
                doc = getattr(self, command).__doc__.strip()
                print('make.py %s [arg]\n\n        %s' % (command, doc))
                print()
            else:
                sys.exit('Cannot show help on unknown command: "%s"' % command)

        else:
            print(__doc__.strip() + '\n\nCommands:\n')
            for command in sorted(dir(self)):
                if command.startswith('_'):
                    continue
                preamble = command.ljust(11)  # longest command is 9 or 10
                # doc = getattr(self, command).__doc__.splitlines()[0].strip()
                doc = getattr(self, command).__doc__.strip()
                print(' %s  %s' % (preamble, doc))
            print()

    def test(self, arg):
        """ Run tests:
                * full - run all tests
                * unit - run tests (also for each backend)
                * any backend name (e.g. pyside2, pyside6, pyqt5, etc.) -
                  run tests for the given backend
                * nobackend - run tests that do not require a backend
                * extra - run extra tests (line endings and style)
                * lineendings - test line ending consistency
                * flake - flake style testing (PEP8 and more)
                * docs - test docstring parameters for correctness
                * examples - run all examples
                * examples [examples paths] - run given examples
        """
        # Note: By default, "python make full" *will* produce coverage data,
        # whereas vispy.test('full') will not. This is because users won't
        # really care about coveraged, but developers will.
        if not arg:
            return self.help('test')
        from vispy import test
        try:
            args = arg.split(' ')
            test(args[0], ' '.join(args[1:]), coverage=True)
        except Exception as err:
            print(err)
            if not isinstance(err, RuntimeError):
                type_, value, tb = sys.exc_info()
                traceback.print_exception(type, value, tb)
            raise SystemExit(1)


if __name__ == '__main__':
    START_DIR = op.abspath(os.getcwd())
    try:
        m = Maker(sys.argv)
    finally:
        os.chdir(START_DIR)
