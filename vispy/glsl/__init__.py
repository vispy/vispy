# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import os
import os.path as op

from .. import config


def find(name):
    """Locate a filename into the shader library."""
    if op.exists(name):
        return name

    path = op.dirname(__file__) or '.'

    paths = [path] + config['include_path']

    for path in paths:
        filename = op.abspath(op.join(path, name))
        if op.exists(filename):
            return filename

        for d in os.listdir(path):
            fullpath = op.abspath(op.join(path, d))
            if op.isdir(fullpath):
                filename = op.abspath(op.join(fullpath, name))
                if op.exists(filename):
                    return filename

    return None


def get(name):
    """Retrieve code from the given filename."""
    filename = find(name)
    if filename is None:
        raise RuntimeError('Could not find %s' % name)
    with open(filename) as fid:
        return fid.read()
