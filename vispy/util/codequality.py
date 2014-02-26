# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Functionality related to code quality.
This module is not imported by default.
"""

import os
import vispy

# Select root dir. Try the real repo root, take the package dir otherwise
ROOT_DIR = os.path.dirname(os.path.dirname(vispy.__file__))
if not os.path.join(ROOT_DIR, 'make', 'make.py'):
    ROOT_DIR = os.path.join(ROOT_DIR, 'vispy')


def check_line_endings():
    """ Check all files in the repository for CR characters.
    Print a report and return the number of affected files.
    """

    report = []

    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        for fname in filenames:
            if os.path.splitext(fname)[1] in ('.pyc', '.pyo',
                                              '.so', '.dll'):
                continue
            # Get filename
            filename = os.path.join(dirpath, fname)
            relfilename = os.path.relpath(filename, ROOT_DIR)
            # Open and check
            try:
                text = open(filename, 'rb').read().decode('utf-8')
            except UnicodeDecodeError:
                continue  # Probably a binary file
            crcount = text.count('\r')
            if crcount:
                lfcount = text.count('\n')
                report.append('In %s found %i/%i CR/LF' %
                              (relfilename, crcount, lfcount))

    # Process result
    nfiles = len(report)
    if nfiles:
        print('\n'.join(report))
        print('Found %i files with CR characters.' % nfiles)
    else:
        print('Verified that all files use LF only.')
    return nfiles
