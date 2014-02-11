# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import print_function, division, absolute_import

import numpy as np
from ..shaders.composite import Function, FunctionChain
from ..util.ordereddict import OrderedDict
from ..util import transforms


class Transform(object):
    """
    Transform is a base class that defines a pair of complementary 
    coordinate mapping functions in both python and GLSL.
    
    All Transform subclasses define map() and imap() methods that map 
    an object through the forward or inverse transformation, respectively.
    
    Note that although all classes should define both map() and imap(), it
    is not necessarily the case that imap(map(x)) == x; there may be instances
    where the inverse mapping is ambiguous or otherwise meaningless.
    
    The two class variables GLSL_map and GLSL_imap are instances of 
    shaders.composite.Function or shaders.composite.FunctionTemplate that
    define the forward- and inverse-mapping GLSL function code.
    
    """
    GLSL_map = None  # Must be Function instance
    GLSL_imap = None
    
    def map(self, obj):
        raise NotImplementedError()
    
    def imap(self, obj):
        raise NotImplementedError()

    def bind_map(self, name, var_prefix=None):
        """
        Return a BoundFunction that accepts only a single vec4 argument,
        with all others bound to new attributes or uniforms.
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
        
        # map all extra args to uniforms
        uniforms = {}
        for arg_type, arg_name in function.args[1:]:
            uniforms[arg_name] = ('uniform', arg_type, var_prefix+arg_name)
        
        
        # bind to a new function + variables
        bound = function.bind(name, **uniforms)
        
        # set uniform values based on properties having same name as 
        # bound argument
        for arg_type, arg_name in function.args[1:]:
            bound[var_prefix+arg_name] = getattr(self, arg_name)
        
        
        return bound


def arg_to_array(func):
    """
    Decorator to convert argument to array.
    """
    def fn(self, arg):
        return func(self, np.array(arg))
    return fn


def as_vec4(obj):
    obj = np.array(obj)
    
    # If this is a single vector, reshape to (1, 4)
    if obj.ndim == 1:
        obj = obj[np.newaxis, :]
        
    # For multiple vectors, reshape to (..., 4)
    if obj.shape[-1] < 4:
        new = np.zeros(obj.shape[:-1] + (4,), dtype=obj.dtype)
        new[...,:obj.shape[-1]] = obj
        obj = new
    elif obj.shape[-1] > 4:
        raise TypeError("Array shape %s cannot be converted to vec4" % obj.shape)
    
    return obj


def arg_to_vec4(func):
    """
    Decorator for converting argument to vec4 format suitable for 4x4 matrix 
    multiplication.
    
    [x, y]      =>  [[x, y, 0, 1]]
    
    [x, y, z]   =>  [[x, y, z, 1]]
    
    [[x1, y1],      [[x1, y1, 0, 1],
     [x2, y2],  =>   [x2, y2, 0, 1],
     [x3, y3]]       [x3, y3, 0, 1]]
     
    If 1D input is provided, then the return value will be flattened.
    Accepts input of any dimension, as long as shape[-1] <= 4
    """
    def fn(self, arg, *args, **kwds):
        arg = np.array(arg)
        flatten = arg.ndim == 1
        arg = as_vec4(arg)
        
        
        # force 1 in last column (is this a bad idea?)
        arg[...,3] = 1
        
        ret = func(self, arg, *args, **kwds)
        if flatten and ret is not None:
            return ret.flatten()
        return ret
    return fn

class TransformChain(Transform):
    """
    Transform subclass that performs a sequence of transformations in order.
    Internally, this class uses shaders.composite.FunctionChain to generate
    its GLSL_map and GLSL_imap functions.
    
    Arguments:
    
    transforms : list of Transform instances
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
        if imap:
            transforms = self.transforms[::-1]
        else:
            transforms = self.transforms
        
        bindings = []
        for i,tr in enumerate(transforms):
            
            tr_name = '%s_%d_%s' % (name, i, type(tr).__name__)
            if imap:
                bound = tr.bind_imap(tr_name)
            else:
                bound = tr.bind_map(tr_name)
            bindings.append(bound)
            
        return FunctionChain(name, bindings)
            



class NullTransform(Transform):
    """ Transform having no effect on coordinates (identity transform).
    """
    GLSL_map = Function("vec4 NullTransform_map(vec4 pos) {return pos;}")
    GLSL_imap = Function("vec4 NullTransform_imap(vec4 pos) {return pos;}")

    def map(self, obj):
        return obj
    
    def imap(self, obj):
        return obj


class STTransform(Transform):
    """ Transform performing only scale and translate
    """
    GLSL_map = Function("""
        vec4 STTransform_map(vec4 pos, vec3 scale, vec3 translate) {
            return (pos * vec4(scale, 1)) + vec4(translate, 0);
        }
    """)
    
    GLSL_imap = Function("""
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
    
    @arg_to_array
    def map(self, coords):
        n = coords.shape[-1]
        return coords * self.scale[:n] + self.translate[:n]
    
    @arg_to_array
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
    GLSL_map = Function("""
        vec4 AffineTransform_map(vec4 pos, mat4 matrix) {
            return matrix * pos;
        }
    """)
    
    GLSL_imap = Function("""
        vec4 AffineTransform_map(vec4 pos, mat4 inv_matrix) {
            return inv_matrix * pos;
        }
    """)
    
    def __init__(self):
        super(AffineTransform, self).__init__()
        self.reset()
    
    @arg_to_vec4
    def map(self, coords):
        # looks backwards, but both matrices are transposed.
        return np.dot(coords, self.matrix)
    
    @arg_to_vec4
    def imap(self, coords):
        return np.dot(coords, self.inv_matrix)

    @property
    def matrix(self):
        return self._matrix
    
    @matrix.setter
    def matrix(self, m):
        self._matrix = m
        self._inv_matrix = None

    @property
    def inv_matrix(self):
        if self._inv_matrix is None:
            self._inv_matrix = np.linalg.inv(self.matrix)
        return self._inv_matrix

    @arg_to_vec4
    def translate(self, pos):
        #tr = np.eye(4)
        #tr[3, :pos.shape[-1]] = pos
        #self.matrix = np.dot(tr, self.matrix)
        self.matrix = transforms.translate(self.matrix, *pos[0,:3])
        
    @arg_to_vec4
    def scale(self, scale, center=None):
        #tr = np.eye(4)
        #for i,s in enumerate(scale[0,:3]):
            #tr[i,i] = s
        #self.matrix = np.dot(tr, self.matrix)
        if center is not None:
            center = as_vec4(center)[0,:3]
            m = transforms.translate(self.matrix, *(-center))
            m = transforms.scale(m, *scale[0,:3])
            m = transforms.translate(self.matrix, *center)
            self.matrix = m
            
        else:
            self.matrix = transforms.scale(self.matrix, *scale[0,:3])

    def rotate(self, angle, axis):
        tr = transforms.rotate(np.eye(4), angle, *axis)
        self.matrix = np.dot(tr, self.matrix)

    def reset(self):
        self.matrix = np.eye(4)
        
    
class SRTTransform(Transform):
    """ Transform performing scale, rotate, and translate
    """
    # TODO

    
class ProjectionTransform(Transform):
    
    # TODO
    
    @classmethod
    def frustum(cls, l, r, t, b, n, f):
        pass


class LogTransform(Transform):
    """ Transform perfoming logarithmic transformation on three axes.
    Maps (x, y, z) => (log(base.x, x), log(base.y, y), log(base.z, z))
    
    No transformation is applied for axes with base <= 0.
    """
    
    # TODO: Evaluate the performance costs of using conditionals. 
    # An alternative approach is to transpose the vector before log-transforming,
    # and then transpose back afterward.
    GLSL_map = Function("""
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
        
    @property
    def base(self):
        """
        *base* is a tuple (x, y, z) containing the log base that should be 
        applied to each axis of the input vector. If any axis has a base <= 0,
        then that axis is not affected.
        """
        return self._base.copy()
    
    @base.setter
    def base(self, s):
        self._base[:len(s)] = s
        self._base[len(s):] = 0.0
            
    @arg_to_array
    def map(self, coords):
        ret = np.empty(coords.shape, coords.dtype)
        base = self.base
        for i in range(ret.shape[-1]):
            if base[i] > 1.0:
                ret[...,i] = np.log(coords[...,i]) / np.log(base[i])
            else:
                ret[...,i] = coords[...,i]
        return ret
    
    @arg_to_array
    def imap(self, coords):
        ret = np.empty(coords.shape, coords.dtype)
        base = self.base
        for i in range(ret.shape[-1]):
            if base[i] > 1.0:
                ret[...,i] = base[i] ** coords[...,i]
            else:
                ret[...,i] = coords[...,i]
        return ret
            
    def __repr__(self):
        return "<LogTransform base=%s>" % (self.base)


class PolarTransform(Transform):
    """
    Polar transform maps (theta, r, ...) to (x, y, ...)
    
    """
    GLSL_map = Function("""
        vec4 PolarTransform_map(vec4 pos) {
            return vec4(pos.y * cos(pos.x), pos.y * sin(pos.x), pos.z, 1);
        }
        """)

    @arg_to_array
    def map(self, coords):
        ret = np.empty(coords.shape, coords.dtype)
        ret[...,0] = coords[...,1] * np.cos[coords[...,0]]
        ret[...,1] = coords[...,1] * np.sin[coords[...,0]]
        for i in range(2, coords.shape[-1]): # copy any further axes
            ret[...,i] = coords[...,i]
        return ret
    
    @arg_to_array
    def imap(self, coords):
        ret = np.empty(coords.shape, coords.dtype)
        ret[...,0] = np.atan2(coords[...,0], np.sin[coords[...,1]])
        ret[...,1] = (coords[...,0]**2 + coords[...,1]**2) ** 0.5
        for i in range(2, coords.shape[-1]): # copy any further axes
            ret[...,i] = coords[...,i]
        return ret
            
    
class BilinearTransform(Transform):
    # TODO
    pass


class WarpTransform(Transform):
    """ Multiple bilinear transforms in a grid arrangement.
    """
    # TODO
