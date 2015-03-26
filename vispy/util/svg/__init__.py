# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
from . svg import SVG
from . path import Path  # noqa
from . base import namespace
from xml.etree import ElementTree


def Document(filename):
    tree = ElementTree.parse(filename)
    root = tree.getroot()
    if root.tag != namespace + 'svg':
        text = 'File "%s" does not seem to be a valid SVG file' % filename
        raise TypeError(text)
    return SVG(root)
