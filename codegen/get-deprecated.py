#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Get deprecated funcsions by parsing gl.spec.

gl.spec is not included in the repo for reasons of space. But you can
easily download it.
"""

import os
import sys

THISDIR = os.path.abspath(os.path.dirname(__file__))

# Load text
filename = os.path.join(THISDIR, 'headers', 'gl.spec')
text = open(filename, 'rb').read().decode('utf-8')

# Define chars that a function name must begin with
chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
assert len(chars) == 26


# Get deprecated functions

deprecated = set()

currentFunc = None
for line in text.splitlines():
    if line.endswith(')') and '(' in line and line[0] in chars:
        currentFunc = line.split('(')[0]
    
    elif not currentFunc:
        pass
    
    elif line.startswith('\t'):
        line = line.replace('\t', ' ')
        parts = line.split(' ')
        parts = [part.strip() for part in parts]
        parts = [part for part in parts if part]
        key = parts[0]
        if len(parts) > 1 :
            val, comment = parts[1], parts[2:]
        if key == 'deprecated' and float(val) <= 3.1:
            deprecated.add(currentFunc)


assert 'Begin' in deprecated


# Print

print('='*80)

pendingline = '    '
for name in sorted(deprecated):
    name = 'gl' + name
    if len(pendingline) + len(name) < 77:
        pendingline += name + ', '
    else:
        print(pendingline)
        pendingline = '    ' + name + ', '
print(pendingline)
print('='*80)

# Report
print('Found %i deprecated functions' % len(deprecated) )
