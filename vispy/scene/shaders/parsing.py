# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import re

# regular expressions for parsing GLSL
re_type = r'(?:void|int|float|vec2|vec3|vec4|mat2|mat3|mat4)'
re_identifier = r'(?:[a-zA-Z_][\w_]*)'

# template variables like
#     $func_name
re_template_var = (r"(?:(?:\$" + re_identifier + ")|(?:\$\{"
                   + re_identifier + "\}))")

# function names may be either identifier or template var
re_func_name = r"(" + re_identifier + "|" + re_template_var + ")"

# type and identifier like "vec4 var_name"
re_declaration = "(?:(" + re_type + ")\s+(" + re_identifier + "))"

# qualifier, type, and identifier like "uniform vec4 var_name"
re_prog_var_declaration = ("(?:(uniform|attribute|varying)\s*(" + re_type +
                           ")\s+(" + re_identifier + "))")

# list of variable declarations like "vec4 var_name, float other_var_name"
re_arg_list = "(" + re_declaration + "(?:,\s*" + re_declaration + ")*)?"

# function declaration like "vec4 function_name(float x, float y)"
re_func_decl = ("(" + re_type + ")\s+" + re_func_name + "\s*\((void|" +
                re_arg_list + ")\)")

# anonymous variable declarations may or may not include a name:
#  "vec4" or "vec4 var_name"
re_anon_decl = "(?:(" + re_type + ")(?:\s+" + re_identifier + ")?)"

# list of anonymous declarations
re_anon_arg_list = "(" + re_anon_decl + "(?:,\s*" + re_anon_decl + ")*)?"

# function prototype declaration like
#    "vec4 function_name(float, float);"
re_func_prot = ("(" + re_type + ")\s+" + re_func_name + "\((void|" +
                re_anon_arg_list + ")\)\s*;")


def parse_function_signature(code):
    """
    Return the name, arguments, and return type of the first function
    definition found in *code*. Arguments are returned as [(type, name), ...].
    """
    m = re.search("^\s*" + re_func_decl + "\s*{", code, re.M)
    if m is None:
        print(code)
        raise Exception("Failed to parse function signature. "
                        "Full code is printed above.")
    rtype, name, args = m.groups()[:3]
    if args == 'void' or args.strip() == '':
        args = []
    else:
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
        m = re.match("\s*" + re_func_prot, line)
        if m is not None:
            rtype, name, args = m.groups()[:3]
            if args == 'void' or args.strip() == '':
                args = []
            else:
                args = [tuple(arg.strip().split(' '))
                        for arg in args.split(',')]
            prots.append((name, args, rtype))

    return prots


def find_program_variables(code):
    """
    Return a dict describing program variables::

        {'var_name': ('uniform|attribute|varying', type), ...}

    """
    vars = {}
    lines = code.split('\n')
    for line in lines:
        m = re.match("\s*" + re_prog_var_declaration + "\s*;", line)
        if m is not None:
            vtype, dtype, name = m.groups()
            vars[name] = (vtype, dtype)
    return vars


def find_template_variables(code):
    """
    Return a list of template variables found in *code*.

    """
    return re.findall(re_template_var, code)
