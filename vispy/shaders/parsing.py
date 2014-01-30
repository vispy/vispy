# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import print_function, division, absolute_import

import re

# regular expressions for parsing GLSL
re_type = r'(void|int|float|vec2|vec3|vec4|mat2|mat3|mat4)'
re_identifier = r'([\w_]+)'
re_declaration = "(?:" + re_type + "\s+" + re_identifier + ")"
re_decl_list = "(" + re_declaration + "(?:,\s*" + re_declaration + ")*)?"
re_func_decl = re_type + "\s+" + re_identifier + "\(" + re_decl_list + "\)"


def parse_function_signature(code):
    """ 
    Return the name, arguments, and return type of the first function 
    definition found in *code*. Arguments are returned as [(type, name), ...].
    """
    m = re.match("\s*" + re_func_decl + "\s*{", code, re.M)
    if m is None:
        print(code)
        raise Exception("Failed to parse function signature. Full code is printed above.")
    rtype, name, args = m.groups()[:3]
    args = [tuple(arg.strip().split(' ')) for arg in args.split(',')]
    return name, args, rtype

def find_prototypes(code):
    """
    Return a list of signatures for each function prototype declared in *code*.
    Format is [(name, [args], rtype), ...].
    """
    
    prots = []
    lines = code.split('\n')
    for line in lines:
        m = re.match("\s*" + re_func_decl + "\s*;", line)
        if m is not None:
            rtype, name, args = m.groups()[:3]
            args = [tuple(arg.strip().split(' ')) for arg in args.split(',')]
            prots.append((name, args, rtype))
    
    return prots
    
