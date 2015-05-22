# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import re

# regular expressions for parsing GLSL
re_type = r'(?:void|int|float|vec2|vec3|vec4|mat2|mat3|mat4|\
            sampler1D|sampler2D|sampler3D)'
re_identifier = r'(?:[a-zA-Z_][\w_]*)'

# variable qualifiers
re_qualifier = r'(const|uniform|attribute|varying)'

# template variables like
#     $func_name
re_template_var = (r"(?:(?:\$" + re_identifier + ")|(?:\$\{" +
                   re_identifier + "\}))")

# function names may be either identifier or template var
re_func_name = r"(" + re_identifier + "|" + re_template_var + ")"

# type and identifier like "vec4 var_name"
re_declaration = "(?:(" + re_type + ")\s+(" + re_identifier + "))"

# qualifier, type, and identifier like "uniform vec4 var_name"
# qualifier is optional.
# may include multiple names like "attribute float x, y, z"
re_prog_var_declaration = ("(?:" + re_qualifier + "?\s*(" + re_type +
                           ")\s+(" + re_identifier + "(\s*,\s*(" +
                           re_identifier + "))*))")

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


def find_functions(code):
    """
    Return a list of (name, arguments, return type) for all function 
    definition2 found in *code*. Arguments are returned as [(type, name), ...].
    """
    regex = "^\s*" + re_func_decl + "\s*{"
    
    funcs = []
    while True:
        m = re.search(regex, code, re.M)
        if m is None:
            return funcs
        
        rtype, name, args = m.groups()[:3]
        if args == 'void' or args.strip() == '':
            args = []
        else:
            args = [tuple(arg.strip().split(' ')) for arg in args.split(',')]
        funcs.append((name, args, rtype))
        
        code = code[m.end():]


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
        m = re.match(r"\s*" + re_prog_var_declaration + r"\s*(=|;)", line)
        if m is not None:
            vtype, dtype, names = m.groups()[:3]
            for name in names.split(','):
                vars[name.strip()] = (vtype, dtype)
    return vars


def find_template_variables(code):
    """
    Return a list of template variables found in *code*.

    """
    return re.findall(re_template_var, code)
