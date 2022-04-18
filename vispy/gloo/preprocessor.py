
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import re
from .. import glsl
from ..util import logger


def remove_comments(code):
    """Remove C-style comment from GLSL code string."""
    pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*\n)"
    # first group captures quoted strings (double or single)
    # second group captures comments (//single-line or /* multi-line */)
    regex = re.compile(pattern, re.MULTILINE | re.DOTALL)

    def do_replace(match):
        # if the 2nd group (capturing comments) is not None,
        # it means we have captured a non-quoted (real) comment string.
        if match.group(2) is not None:
            return ""  # so we will return empty to remove the comment
        else:  # otherwise, we will return the 1st group
            return match.group(1)  # captured quoted-string

    return regex.sub(do_replace, code)


def merge_includes(code):
    """Merge all includes recursively."""
    pattern = r'\#\s*include\s*"(?P<filename>[a-zA-Z0-9\_\-\.\/]+)"'
    regex = re.compile(pattern)
    includes = []

    def replace(match):
        filename = match.group("filename")

        if filename not in includes:
            includes.append(filename)
            path = glsl.find(filename)
            if not path:
                logger.critical('"%s" not found' % filename)
                raise RuntimeError("File not found", filename)
            text = '\n// --- start of "%s" ---\n' % filename
            with open(path) as fh:
                text += fh.read()
            text += '// --- end of "%s" ---\n' % filename
            return text
        return ''

    # Limit recursion to depth 10
    for i in range(10):
        if re.search(regex, code):
            code = re.sub(regex, replace, code)
        else:
            break

    return code


def preprocess(code):
    """Preprocess a code by removing comments, version and merging includes."""
    if code:
        # code = remove_comments(code)
        code = merge_includes(code)
    return code
