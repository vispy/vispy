# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import os


def find(name):
    """Locate a filename into the shader library."""

    if os.path.exists(name):
        return name

    path = os.path.dirname(__file__) or '.'

    from vispy import config
    paths = [path] + config['include_path']

    filename = os.path.abspath(os.path.join(path, name))
    if os.path.exists(filename):
        return filename

    for d in os.listdir(path):
        fullpath = os.path.abspath(os.path.join(path, d))
        if os.path.isdir(fullpath):
            filename = os.path.abspath(os.path.join(fullpath, name))
            if os.path.exists(filename):
                return filename
    return None


def get(name):
    """Retrieve code from the given filename."""

    filename = find(name)
    if filename is None:
        return name
    with open(filename) as fid:
        return fid.read()
