# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import print_function, division, absolute_import

from ..gloo import Program
from .parsing import parse_function_signature

class ShaderFunction:
    def __init__(self, code, name=None, args=None, rtype=None):
        """
        *args* must be a list of ('type', 'name') tuples.        
        """
        self.code = code
        if name is None:
            self.name, self.args, self.rtype = parse_function_signature(self.code)
        else:
            self.name = name
            self.args = args
            self.rtype = rtype
        self._arg_types = dict([(a[1], a[0]) for a in self.args])
        
                    
    def bind(self, name, attributes=None, uniforms=None, varyings=None):
        """
        Return GLSL code for a new function with *name* that replaces
        some of the arguments to the original function with attributes or
        uniforms.
        
        This is analogous to python bound methods, where the first argument
        is replaced by an instance (but in this case, any argument(s) may be
        bound to uniforms or attributes).
        
        The primary purpose of this is to allow multiple instances of the same
        ShaderFunction to be used in the final program, where each instance
        generates a new function with unique attribute/uniform names. 
        
        *attributes* and *uniforms* args must be dicts like 
        {'arg_name': 'attr_name'}
        
        
        For example, if the original function signature looks like:
        
            vec4 my_function(float a, vec2 b, vec3 c)
            
        Then the following bind call:
        
            func.bind('new_func_name', 
                      attributes={'b': 'input_b'}, 
                      uniforms={'c': 'input_c'})
                      
        Would return the following new function code:
        
            attribute vec2 input_b;
            uniform vec3 input_c;
            vec4 new_func_name(float a) {
                return my_function(a, input_b, input_c);
            }
        
        """
        attributes = {} if attributes is None else attributes
        uniforms = {} if uniforms is None else uniforms
        varyings = {} if varyings is None else varyings
        
        code = ""
        
        # Generate attribute/uniform declarations
        for arg, attr in attributes.items():
            typ = self._arg_types[arg]
            code += "attribute %s %s;\n" % (typ, attr)
        for arg, uni in uniforms.items():
            typ = self._arg_types[arg]
            code += "uniform %s %s;\n" % (typ, uni)
        for arg, var in varyings.items():
            typ = self._arg_types[arg]
            code += "varying %s %s;\n" % (typ, var)
        code += "\n"
        
        # new function signature
        arg_defs = ["%s %s" % x for x in self.args[:] if x[1] not in attributes and x[1] not in uniforms and x[1] not in varyings]
        new_sig = ", ".join(arg_defs)
        code += "%s %s(%s) {\n" % (self.rtype, name, new_sig)
        
        # call original function
        args = []
        for atyp, argname in self.args:
            if argname in attributes:
                args.append(attributes[argname])
            elif argname in uniforms:
                args.append(uniforms[argname])
            elif argname in varyings:
                args.append(varyings[argname])
            else:
                args.append(argname)
        code += "    return %s(%s);\n" % (self.name, ", ".join(args))
        
        code += "}\n"
        
        return code

