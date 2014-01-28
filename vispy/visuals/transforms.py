# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import print_function, division, absolute_import

import numpy as np
from ..shaders.composite import ShaderFunction
from ..util.ordereddict import OrderedDict
from ..util import transforms

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
        
        3) A dict containing function definitions that are required by this 
        transform; the program constructor should ensure that each function is 
        only included in the program once.
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
        
        defs = {function.name: function.code}
        
        return code, values, defs


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
        defs = OrderedDict()
        if imap:
            transforms = self.transforms[::-1]
        else:
            transforms = self.transforms
        
        for i,tr in enumerate(transforms):
            tr_name = '%s_%s_%d' % (name, type(tr).__name__, i)
            if imap:
                tr_code, tr_vars, tr_defs = tr.bind_imap(tr_name)
            else:
                tr_code, tr_vars, tr_defs = tr.bind_map(tr_name)
            bindings.append(tr_code)
            variables.update(tr_vars)
            defs.update(tr_defs)
            code += "    pos = %s(pos);\n" % tr_name
        code += "    return pos;\n}\n"
        
        code = "\n".join(bindings) + "\n\n" + code
        
        
        return code, variables, defs
            



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




class AffineTransform(Transform):
    GLSL_map = ShaderFunction("""
        vec4 AffineTransform_map(vec4 pos, mat4 matrix) {
            return matrix * pos;
        }
    """)
    
    GLSL_imap = ShaderFunction("""
        vec4 AffineTransform_map(vec4 pos, mat4 inv_matrix) {
            return inv_matrix * pos;
        }
    """)
    
    def __init__(self):
        super(AffineTransform, self).__init__()
        self.reset()
    
    def map(self, coords):
        return np.dot(self.matrix, coords)
    
    def imap(self, coords):
        return np.dot(self.inv_matrix, coords)

    @property
    def matrix(self):
        return self._matrix
    
    @matrix.setter
    def matrix(self, m):
        self._matrix = m

    @property
    def inv_matrix(self):
        if self._inv_matrix is None:
            self.inv_matrix = np.linalg.invert(self.matrix)
        return self._inv_matrix

    def translate(self, pos):
        tr = np.eye(4)
        tr[3, :len(pos)] = pos
        self.matrix = np.dot(tr, self.matrix)
        #self.matrix = transforms.translate(self.matrix, *pos)
        print(self.matrix)
        self._inv_matrix = None
        
    def scale(self, scale):
        tr = np.eye(4)
        for i,s in enumerate(scale):
            tr[i,i] = s
        self.matrix = np.dot(tr, self.matrix)
        #self.matrix = transforms.scale(self.matrix, *scale)
        print(self.matrix)
        self._inv_matrix = None

    def rotate(self, angle, axis):
        tr = transforms.rotate(np.eye(4), angle, *axis)
        self.matrix = np.dot(tr, self.matrix)
        print(self.matrix)
        self._inv_matrix = None

    def reset(self):
        self.matrix = np.eye(4)
        self._inv_matrix = None
        
    
class SRTTransform(Transform):
    """ Transform performing scale, rotate, and translate
    """
    
class ProjectionTransform(Transform):
    @classmethod
    def frustum(cls, l, r, t, b, n, f):
        pass

class LogTransform(Transform):
    """ Transform perfoming logarithmic transformation on three axes.
    """
    GLSL_map = ShaderFunction("""
        vec4 LogTransform_map(vec4 pos, vec3 base) {
            vec4 p1 = pos;
            if(base.x > 1.0)
                p1.x = log(p1.x) / log(base.x);
            if(base.y > 1.0)
                p1.y = log(p1.y) / log(base.y);
            if(base.z > 1.0)
                p1.z = log(p1.z) / log(base.z);
            return p1;
        }
        """)
    
    def __init__(self, base=None):
        super(LogTransform, self).__init__()
        self._base = np.zeros(3, dtype=np.float32)
        self.base = (0.0, 0.0, 0.0) if base is None else base
        
    def map(self, coords):
        ret = np.empty(coords.shape, coords.dtype)
        base = self.base
        for i in range(ret.shape[-1]):
            if base[i] > 1.0:
                ret[...,i] = np.log(coords[...,i]) / np.log(base[i])
            else:
                ret[...,i] = coords[...,i]
        return ret
    
    def imap(self, coords):
        ret = np.empty(coords.shape, coords.dtype)
        base = self.base
        for i in range(ret.shape[-1]):
            if base[i] > 1.0:
                ret[...,i] = base[i] ** coords[...,i]
            else:
                ret[...,i] = coords[...,i]
        return ret
            
    @property
    def base(self):
        return self._base.copy()
    
    @base.setter
    def base(self, s):
        self._base[:len(s)] = s
        self._base[len(s):] = 0.0
            
    def __repr__(self):
        return "<LogTransform base=%s>" % (self.base)

class PolarTransform(Transform):
    pass

class BilinearTransform(Transform):
    pass

class WarpTransform(Transform):
    """ Multiple bilinear transforms in a grid arrangement.
    """
