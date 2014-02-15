# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import print_function, division, absolute_import

import numpy as np
from ..shaders.composite import Function, FunctionChain, FunctionTemplate
from ..util.ordereddict import OrderedDict
from ..util import transforms

"""
API Issues to work out:

  - Should transforms within a chain be treated as mutable? 
  
        t1 = STTransform(...)
        t2 = AffineTransform(...)
        ct = ChainTransform([t1, t2])
        
        t1.scale = (0.5, 0.5) # should this affect ChainTransform?
        
  - Should transform multiplication work like matrix multiplication?
    (and should we use __mul__ at all?)
    
        t1 * t2  => ChainTransform([t2, t1])  
                        OR
                 => ChainTransform([t1, t2])
                 
    Matrix-multiplication style is tempting, but confounded by the fact 
    that throughout vispy, we use transformation matrices and vectors that are 
    transposed relative to traditional linear algebra expectations. This has the 
    awkward side-effect that the arguments to np.dot() must be reversed (and 
    potentially other side effects). Since we are reversing the matrix 
    multiplication order anyway, perhaps it makes sense to reverse it here as 
    well?

  - Should transforms have a 'changed' event?
  
        t1.changed.connect(callback)
            OR
        t1.events.change.connect(callback)
        
  - AffineTransform and STTransform both have 'scale' and 'translate'
    attributes, but they are used in very different ways. It would be nice
    to keep this consistent, but how?
"""




class Transform(object):
    """
    Transform is a base class that defines a pair of complementary 
    coordinate mapping functions in both python and GLSL.
    
    All Transform subclasses define map() and imap() methods that map 
    an object through the forward or inverse transformation, respectively.
    
    The two class variables GLSL_map and GLSL_imap are instances of 
    shaders.composite.Function or shaders.composite.FunctionTemplate that
    define the forward- and inverse-mapping GLSL function code.
    
    Optionally, an inverse() method returns a new Transform performing the
    inverse mapping.
    
    Note that although all classes should define both map() and imap(), it
    is not necessarily the case that imap(map(x)) == x; there may be instances
    where the inverse mapping is ambiguous or otherwise meaningless.
    
    
    """
    GLSL_map = None  # Must be Function instance
    GLSL_imap = None
    
    def map(self, obj):
        """
        Return *obj* mapped through the forward transformation.
        
        Parameters:
            obj : tuple (x,y) or (x,y,z)
                  array with shape (..., 2) or (..., 3)
        """
        raise NotImplementedError()
    
    def imap(self, obj):
        """
        Return *obj* mapped through the inverse transformation.
        
        Parameters:
            obj : tuple (x,y) or (x,y,z)
                  array with shape (..., 2) or (..., 3)
        """
        raise NotImplementedError()
    
    def inverse(self):
        """
        Return a new Transform that performs the inverse mapping of this 
        transform.
        """
        raise NotImplementedError()

    def bind_map(self, name, var_prefix=None):
        """
        Return a Function that accepts only a single vec4 argument and defines
        new attributes / uniforms supplying the Function with any static input.
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
        #for arg_type, arg_name in function.args[1:]:
        for var_name in function.bindings:
            if var_name == function.args[0][1]:
                continue
            uniforms[var_name] = ('uniform', var_prefix+var_name)
        
        # bind to a new function + variables
        bound = function.bind(name, **uniforms)
        
        # set uniform values based on properties having same name as 
        # bound argument
        for var_name in uniforms:
            bound[var_prefix+var_name] = getattr(self, var_name)
        
        return bound

    def __mul__(self, tr):
        """
        Transform multiplication returns a new Transform that is equivalent to 
        the two operands performed in series.
        
        By default, multiplying two Transforms `A * B` will return 
        ChainTransform([A, B]). Subclasses may redefine this operation to return 
        more optimized results.
        
        To ensure that both operands have a chance to simplify the operation,
        all subclasses should follow the same procedure. For `A * B`:
        
        1. A.__mul__(B) attempts to generate an optimized Transform product.
        2. If that fails, it must:
        
               * return super(A).__mul__(B) OR 
               * return NotImplemented if the superclass would return an invalid
                 result.
                 
        3. When Transform.__mul__(A, B) is called, it returns NotImplemented, 
           which causes B.__rmul__(A) to be invoked.
        4. B.__rmul__(A) attempts to generate an optimized Transform product.
        5. If that fails, it must:
        
               * return super(B).__rmul__(A) OR
               * return ChainTransform([A, B]) if the superclass would return an
                 invalid result.
                 
        6. When Transform.__rmul__(B, A) is called, ChainTransform([B, A]) is 
           returned. Note that the order is reversed so that multiplication
           works like matrix multiplication (last matrix in a product is the
           first to be applied when mapping vectors).
        """
        # switch to __rmul__ attempts.
        return NotImplemented

    def __rmul__(self, tr):
        return ChainTransform([self, tr])
        
    

def arg_to_array(func):
    """
    Decorator to convert argument to array.
    """
    def fn(self, arg):
        return func(self, np.array(arg))
    return fn


def as_vec4(obj, default=(0,0,0,1)):
    """
    Convert *obj* to 4-element vector (numpy array with shape[-1] == 4)
    
    If *obj* has < 4 elements, then new elements are added from *default*.
    For inputs intended as a position or translation, use default=(0,0,0,1).
    For inputs intended as scale factors, use default=(1,1,1,1).
    """
    obj = np.array(obj)
    
    # If this is a single vector, reshape to (1, 4)
    if obj.ndim == 1:
        obj = obj[np.newaxis, :]
        
    # For multiple vectors, reshape to (..., 4)
    if obj.shape[-1] < 4:
        new = np.empty(obj.shape[:-1] + (4,), dtype=obj.dtype)
        new[:] = default
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
    
    Alternatively, any class may define its own transform conversion interface
    by defining a _transform_in() method that returns an array with shape
    (.., 4), and a _transform_out() method that accepts the same array shape 
    and returns a new (mapped) object.
    
    """
    def fn(self, arg, *args, **kwds):
        if type(arg) in (tuple, list, np.ndarray):
            arg = np.array(arg)
            flatten = arg.ndim == 1
            arg = as_vec4(arg)
            
            ret = func(self, arg, *args, **kwds)
            if flatten and ret is not None:
                return ret.flatten()
            return ret
        elif hasattr(arg, '_transform_in'):
            arr = arg._transform_in()
            ret = func(self, arr, *args, **kwds)
            return arg._transform_out(ret)
    return fn


class ChainTransform(Transform):
    """
    Transform subclass that performs a sequence of transformations in order.
    Internally, this class uses shaders.composite.FunctionChain to generate
    its GLSL_map and GLSL_imap functions.
    
    Arguments:
    
    transforms : list of Transform instances
    """
    GLSL_map = ""
    GLSL_imap = ""
    
    def __init__(self, transforms=None, simplify=False):
        super(ChainTransform, self).__init__()
        if transforms is None:
            transforms = []
        self.transforms = transforms
        self.flatten()
        if simplify:
            self.simplify()
        
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
    
    def inverse(self):
        return ChainTransform([tr.inverse() for tr in self.transforms[::-1]])
    
    def flatten(self):
        """
        Attempt to simplify the chain by expanding any nested chains.
        """
        new_tr = []
        for tr in self.transforms:
            if isinstance(tr, ChainTransform):
                new_tr.extend(tr.transforms)
            else:
                new_tr.append(tr)
        self.transforms = new_tr
    
    def simplify(self):
        """
        Attempt to simplify the chain by joining adjacent transforms.        
        """
        self.flatten()
        while True:
            new_tr = [self.transforms[0]]
            exit = True
            for t2 in self.transforms[1:]:
                t1 = new_tr[-1]
                pr = t1 * t2
                if not isinstance(pr, ChainTransform):
                    exit = False
                    new_tr.pop()
                    new_tr.append(pr)
                else:
                    new_tr.append(tr2)
            self.transforms = new_tr
            if exit:
                break
            

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

    def append(self, tr):
        """
        Add a new Transform to the end of this chain, combining with prior
        transforms if possible.        
        """
        while len(self.transforms) > 0:
            pr = tr * self.transforms[-1]
            if isinstance(pr, ChainTransform):
                self.transforms.append(tr)
                break
            else:
                self.transforms.pop()
                tr = pr
                if len(self.transforms)  == 0:
                    self.transforms = [pr]
                    break

    def prepend(self, tr):
        """
        Add a new Transform to the beginning of this chain, combining with 
        subsequent transforms if possible.        
        """
        while len(self.transforms) > 0:
            pr = self.transforms[0] * tr
            if isinstance(pr, ChainTransform):
                self.transforms.insert(0, tr)
                break
            else:
                self.transforms.pop(0)
                tr = pr
                if len(self.transforms)  == 0:
                    self.transforms = [pr]
                    break
    
    def __mul__(self, tr):
        if isinstance(tr, ChainTransform):
            trs = tr.transforms
        else:
            trs = [tr]
            
        new = ChainTransform(self.transforms)
        for t in trs:
            new.prepend(t)
        return new
        
    def __rmul__(self, tr):
        new = ChainTransform(self.transforms)
        new.append(tr)
        return new
        
    def __repr__(self):
        names = [tr.__class__.__name__ for tr in self.transforms]
        return "<ChainTransform [%s]>" % (", ".join(names))


class NullTransform(Transform):
    """ Transform having no effect on coordinates (identity transform).
    """
    GLSL_map = FunctionTemplate("vec4 $func_name(vec4 pos) {return pos;}")
    GLSL_imap = FunctionTemplate("vec4 $func_name(vec4 pos) {return pos;}")

    def map(self, obj):
        return obj
    
    def imap(self, obj):
        return obj
    
    def inverse(self):
        return NullTransform()

    def __mul__(self, tr):
        return tr
    
    def __rmul__(self, tr):
        return tr
    

class STTransform(Transform):
    """ Transform performing only scale and translate, in that order.
    """
    GLSL_map = FunctionTemplate("""
        vec4 $func_name(vec4 pos) {
            return (pos * $scale) + $translate;
        }
    """, bindings=['vec4 scale', 'vec4 translate'])
    
    GLSL_imap = FunctionTemplate("""
        vec4 $func_name(vec4 pos) {
            return (pos - $translate) / $scale;
        }
    """, bindings=['vec4 scale', 'vec4 translate'])
    
    def __init__(self, scale=None, translate=None):
        super(STTransform, self).__init__()
            
        self._scale = np.ones(4, dtype=np.float32)
        self._translate = np.zeros(4, dtype=np.float32)
        
        self.scale = (1.0, 1.0, 1.0) if scale is None else scale
        self.translate = (0.0, 0.0, 0.0) if translate is None else translate
    
    @arg_to_vec4
    def map(self, coords):
        n = coords.shape[-1]
        return coords * self.scale[:n] + self.translate[:n]
    
    @arg_to_vec4
    def imap(self, coords):
        n = coords.shape[-1]
        return (coords - self.translate[:n]) / self.scale[:n]

    def inverse(self):
        s = 1./self.scale
        t = -self.translate * s
        return STTransform(scale=s, translate=t)
    
    @property
    def scale(self):
        return self._scale.copy()
    
    @scale.setter
    def scale(self, s):
        self._scale[:len(s)] = s[:4]
        self._scale[len(s):] = 1.0
        #self._update()
        
    @property
    def translate(self):
        return self._translate.copy()
    
    @translate.setter
    def translate(self, t):
        self._translate[:len(t)] = t[:4]
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
            return super(STTransform, self).__mul__(tr)

    def __rmul__(self, tr):
        if isinstance(tr, AffineTransform):
            return tr * self.as_affine()
        return super(STTransform, self).__rmul__(tr)
            
    def __repr__(self):
        return "<STTransform scale=%s translate=%s>" % (self.scale, self.translate)




class AffineTransform(Transform):
    GLSL_map = FunctionTemplate("""
        vec4 $func_name(vec4 pos) {
            return $matrix * pos;
        }
    """, bindings=['mat4 matrix'])
    
    GLSL_imap = FunctionTemplate("""
        vec4 $func_name(vec4 pos) {
            return $inv_matrix * pos;
        }
    """, bindings=['mat4 inv_matrix'])
    
    def __init__(self, matrix=None):
        super(AffineTransform, self).__init__()
        if matrix is not None:
            self.matrix = matrix
        else:
            self.reset()
    
    @arg_to_vec4
    def map(self, coords):
        # looks backwards, but both matrices are transposed.
        return np.dot(coords, self.matrix)
    
    @arg_to_vec4
    def imap(self, coords):
        return np.dot(coords, self.inv_matrix)

    def inverse(self):
        tr = AffineTransform()
        try:
            tr.matrix = np.linalg.inv(self.matrix)
        except:
            print(self.matrix)
            raise
        return tr

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
        """
        Translate the matrix by *pos*. 
        
        The translation is applied *after* the transformations already present
        in the matrix.
        """
        self.matrix = transforms.translate(self.matrix, *pos[0,:3])
        
    def scale(self, scale, center=None):
        """
        Scale the matrix by *scale* around the origin *center*. 
        
        The scaling is applied *after* the transformations already present
        in the matrix.
        """
        scale = as_vec4(scale, default=(1,1,1,1))
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
        
    def __mul__(self, tr):
        if isinstance(tr, AffineTransform):
            return AffineTransform(matrix=np.dot(tr.matrix, self.matrix))
        else:
            return tr.__rmul__(self)
            #return super(AffineTransform, self).__mul__(tr)

    def __repr__(self):
        s = "AffineTransform(matrix=["
        indent = " "*len(s)
        s += str(list(self.matrix[0])) + ",\n"
        s += indent + str(list(self.matrix[1])) + ",\n"
        s += indent + str(list(self.matrix[2])) + ",\n"
        s += indent + str(list(self.matrix[3])) + "])"
        return s
    
class SRTTransform(Transform):
    """ Transform performing scale, rotate, and translate, in that order.
    
    This transformation allows objects to be placed arbitrarily in a scene
    much the same way AffineTransform does. However, an incorrect order of
    operations in AffineTransform may result in shearing the object (if scale
    is applied after rotate) or in unpredictable translation (if scale/rotate
    is applied after translation). SRTTransform avoids these problems by
    enforcing the correct order of operations.
    """
    # TODO

    
class PerspectiveTransform(AffineTransform):
    """
    Matrix transform that also implements perspective division.    
    """
    # TODO
    
    @classmethod
    def frustum(cls, l, r, t, b, n, f):
        pass


class OrthoTransform(AffineTransform):
    """
    Orthographic transform
    (possibly no need for this; just add an ortho() method to AffineTransform?)
    """
    # TODO


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
    Polar transform maps (theta, r, z) to (x, y, z), where `x = r*cos(theta)`
    and `y = r*sin(theta)`.
    
    """
    GLSL_map = FunctionTemplate("""
        vec4 $func_name(vec4 pos) {
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
