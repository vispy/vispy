# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import print_function, division, absolute_import

import numpy as np
from ..shaders.composite import ShaderFunction

## TODO: binding should be handled by ShaderFunction? Or perhaps some other type?
class Transform(object):
    """
    Transform is a base class that defines a pair of complementary 
    coordinate mapping functions in both python and GLSL.
    """
    GLSL_map = None  # Must be ShaderFunction instance
    GLSL_imap = None
    
    def map(self, obj):
        raise NotImplementedError()
    
    def imap(self, obj):
        raise NotImplementedError()

    def bind_map(self, name, var_prefix=None):
        """
        Return a tuple containing:
        
        1) Code for a GLSL map function with *name* that accepts only a single
        input argument and binds all other arguments to program 
        uniform/attributes. (see ShaderFunction.bind)
        All uniform/attribute names are prefixed with *var_prefix* to ensure
        uniqueness. If var_prefix is not given, then *name_* is used instead.
        
        2) A dict mapping attribute/uniform names to the values they should
        be assigned in the program.
        """
        if var_prefix is None:
            var_prefix = name + "_"
        return self._bind(name, var_prefix, imap=False)
        
    def bind_imap(self, name, var_prefix=None):
        """
        see bind_map.
        """
        if var_prefix is None:
            var_prefix = name + "_"
        return self._bind(name, var_prefix, imap=True)

    def _bind(self, name, var_prefix, imap):
        # The default implemntation assumes the following:
        # * The first argument to the GLSL function should not be bound
        # * All remaining arguments should be bound using self.property of the
        #   same name to determine the value.
        
        function = self.GLSL_imap if imap else self.GLSL_map
        
        # get names of all arguments after the first
        args = [arg[1] for arg in function.args[1:]]
        
        # map all extra args to uniforms
        uniforms = dict([(arg, var_prefix+arg) for arg in args]) 
        
        # assume there is a self.property with the same name
        values = dict([(var_prefix+arg, getattr(self, arg)) for arg in args])
        
        # bind to a new function + variables
        code = function.bind(name, uniforms=uniforms)
        
        return code, values


## TODO: this should inherit from FunctionChain
class TransformChain(Transform):
    """
    Sequential chain of Transforms.
    
    """
    GLSL_map = ""
    GLSL_imap = ""
    
    def __init__(self, transforms=None):
        super(TransformChain, self).__init__()
        if transforms is None:
            transforms = []
        self.transforms = transforms
        
    @property
    def transforms(self):
        return self._transforms
    
    @transforms.setter
    def transforms(self, tr):
        #if self._enabled:
            #raise RuntimeError("Shader is already enabled; cannot modify.")
        if not isinstance(tr, list):
            raise TypeError("Transform chain must be a list")
        self._transforms = tr
        
    def map(self, obj):
        for tr in self.transforms:
            obj = tr.map(obj)
        return obj

    def imap(self, obj):
        for tr in self.transforms[::-1]:
            obj = tr.imap(obj)
        return obj

    def _bind(self, name, var_prefix, imap):
        code = "vec4 %s(vec4 pos) {\n" % name
        bindings = []
        variables = {}
        if imap:
            transforms = self.transforms[::-1]
        else:
            transforms = self.transforms
        
        for i,tr in enumerate(transforms):
            tr_name = '%s_%s_%d' % (name, type(tr).__name__, i)
            if imap:
                tr_code, tr_vars = tr.bind_imap(tr_name)
            else:
                tr_code, tr_vars = tr.bind_map(tr_name)
            bindings.append(tr_code)
            variables.update(tr_vars)
            code += "    pos = %s(pos);\n" % tr_name
        code += "    return pos;\n}\n"
        
        code = "\n".join(bindings) + "\n\n" + code
        
        return code, variables
            
    ## TODO: this should be handled by component deps instead.
    @property
    def GLSL_map(self):
        trcode = {tr.GLSL_map.name:tr.GLSL_map.code for tr in self.transforms}
        return "\n".join(trcode.values())





class NullTransform(Transform):
    """ Transform having no effect on coordinates (identity transform).
    """
    GLSL_map = ShaderFunction("vec4 NullTransform_map(vec4 pos) {return pos;}")
    GLSL_imap = ShaderFunction("vec4 NullTransform_imap(vec4 pos) {return pos;}")

    def map(self, obj):
        return obj
    
    def imap(self, obj):
        return obj


class STTransform(Transform):
    """ Transform performing only scale and translate
    """
    GLSL_map = ShaderFunction("""
        vec4 STTransform_map(vec4 pos, vec3 scale, vec3 translate) {
            return (pos * vec4(scale, 1)) + vec4(translate, 0);
        }
    """)
    
    GLSL_imap = ShaderFunction("""
        vec4 STTransform_map(vec4 pos, vec3 scale, vec3 translate) {
            return (pos - vec4(translate, 0)) / vec4(scale, 1);
        }
    """)
    
    def __init__(self, scale=None, translate=None):
        super(STTransform, self).__init__()
            
        self._scale = np.ones(3, dtype=np.float32)
        self._translate = np.zeros(3, dtype=np.float32)
        
        self.scale = (1.0, 1.0, 1.0) if scale is None else scale
        self.translate = (0.0, 0.0, 0.0) if translate is None else translate
    
    def map(self, coords):
        n = coords.shape[-1]
        return coords * self.scale[:n] + self.translate[:n]
    
    def imap(self, coords):
        n = coords.shape[-1]
        return (coords - self.translate[:n]) / self.scale[:n]
    
    @property
    def scale(self):
        return self._scale.copy()
    
    @scale.setter
    def scale(self, s):
        self._scale[:len(s)] = s
        self._scale[len(s):] = 1.0
        #self._update()
        
    @property
    def translate(self):
        return self._translate.copy()
    
    @translate.setter
    def translate(self, t):
        self._translate[:len(t)] = t
        self._translate[len(t):] = 0.0
            
    def as_affine(self):
        m = AffineTransform()
        m.scale(self.scale)
        m.translate(self.translate)
        return m
    
    def __mul__(self, tr):
        if isinstance(tr, STTransform):
            s = self.scale * tr.scale
            t = self.translate + (tr.translate * self.scale)
            return STTransform(scale=s, translate=t)
        elif isinstance(tr, AffineTransform):
            return self.as_affine() * tr
        else:
            return NotImplemented
            
    def __repr__(self):
        return "<STTransform scale=%s translate=%s>" % (self.scale, self.translate)
