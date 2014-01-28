# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np

from ..gloo import VertexShader
from ..util import logger


class TransformChain(VertexShader):

    """ Transform shader built from a series of Transform shaders.

    Will collapse adjacent transforms if possible.
    """

    def __init__(self, transforms=None, function=None):
        super(TransformChain, self).__init__()
        if transforms is None:
            transforms = []
        self._transforms = transforms
        self._enabled = True
        self._function = function

    @property
    def transforms(self):
        return self._transforms

    @transforms.setter
    def transforms(self, tr):
        if self._enabled:
            raise RuntimeError("Shader is already enabled; cannot modify.")
        if not isinstance(tr, list):
            raise TypeError("Transform chain must be a list")
        self._transforms = tr

    def append(self, tr):
        if self._enabled:
            raise RuntimeError("Shader is already enabled; cannot modify.")
        self._transforms.append(tr)

    def prepend(self, tr):
        if self._enabled:
            raise RuntimeError("Shader is already enabled; cannot modify.")
        self._transforms.insert(0, tr)

    def _enable(self):
        self._enabled = True
        self.set_source(self._generate_source())
        super(TransformChain, self)._enable()

    def _generate_source(self):
        transform_indexes = {}
        variable_decl = []
        func_calls = []
        for tr in self._transforms[::-1]:
            if tr.function not in transform_indexes:
                ind = 0
                argtypes = ['vec4'] + [d for a, d, n in tr.arguments]
                variable_decl.append(
                    "vec4 %s(%s);\n" %
                    (tr.function, ", ".join(argtypes)))
            else:
                ind = transform_indexes[tr.function]
            transform_indexes[tr.function] = ind + 1
            args = []
            sig_decl = ['vec4']
            for atype, dtype, name in tr.arguments:
                varname = '%s_%s_%d' % (tr.function, name, ind)
                variable_decl.append("%s %s %s;\n" % (atype, dtype, varname))
                # tell the transform the names of uniforms/atributes that will
                # be passed as arguments.
                tr._arg_map[name] = varname
                args.append(varname)
                sig_decl.append(dtype)

            func_calls.append(
                "    pos = %s(pos, %s);\n" %
                (tr.function, ", ".join(args)))

        source = (
            "#version 120\n" +
            "\n" +
            "".join(variable_decl) +
            "\n" +
            "vec4 %s(vec4 pos) {\n" % self._function +
            "".join(func_calls) +
            "    return pos;\n" +
            "}\n")
        logger.debug("====================\n%s" % source)
        return source

    def _disable(self):
        self._enabled = False
        super(TransformChain, self)._disable()

    def _on_attach(self, program):
        attached = set()
        for tr in self.transforms:
            name = tr.function
            if name in attached:
                continue
            attached.add(name)
            program.attach_shader(tr)

    def _on_enabling(self, program):
        super(TransformChain, self)._on_enabling(program)
        for tr in self.transforms:
            tr._apply_variables(program)


class Transform(VertexShader):

    """ Generic template class for vertex transformation shaders

    All Transform classes perform a different type of transformation,
    and include both GLSL and python code for performing the forward
    and reverse mappings.

    In general, transformations should only ever be done using the
    map() and imap() methods. In some cases, imap() may return None.
    """
    source = None    # Default source code for this shader.
    # The name of the mapping function as defined in the shader source.
    function = None
                     # By default, this is set to ClassName_map
    arguments = []   # List of arguments accepted by the mapping function.
                     # The format is (uniform|attribute, type, name)

    def __init__(self, source=None):
        if source is None:
            source = self.__class__.source
        # {argument_name: attribute/uniform_name} set by TransformChain
        self._arg_map = {}
        super(Transform, self).__init__(source)

    def map(self, coords):
        pass

    def imap(self, coords):
        pass

    def __mul__(self, tr):
        # return TransformChain([self, tr])
        return NotImplemented

    def __apply_variables(self, program):
        # Send uniforms/attributes for this transform to currently-enabled
        # program, if any.
        pass


class NullTransform(Transform):

    """ Transform having no effect on coordinates.
    """
    source = """
        #version 120

        vec4 NullTransform_map(vec4 pos) {
            return pos;
        }
        """
    function = 'NullTransform_map'


class STTransform(Transform):

    """ Transform perfoming only scale and translate
    """
    source = """
        #version 120

        vec4 STTransform_map(vec4 pos, vec3 scale, vec3 translate) {
            return (pos * vec4(scale, 1)) + vec4(translate, 0);
        }
        """
    function = 'STTransform_map'
    arguments = [
        ('uniform', 'vec3', 'scale'),
        ('uniform', 'vec3', 'translate'),
    ]

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
        # self._update()

    @property
    def translate(self):
        return self._translate.copy()

    @translate.setter
    def translate(self, t):
        self._translate[:len(t)] = t
        self._translate[len(t):] = 0.0

    def _apply_variables(self, program):
        # Send uniforms to currently-enabled program, if any.
        program.uniforms[self._arg_map['scale']] = self.scale
        program.uniforms[self._arg_map['translate']] = self.translate

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
        return "<STTransform scale=%s translate=%s>" % (
            self.scale, self.translate)


class AffineTransform(Transform):

    def __init__(self):
        self.matrix = np.eye(4)
        self.inverse = None
        Transform.__init__(self, """
            #version 120

            uniform mat4 transform;

            vec4 global_transform(vec4 pos) {
                return transform * pos;
            }
            """)

    def map(self, coords):
        return np.dot(self.matrix, coords)

    def imap(self, coords):
        if self.inverse is None:
            self.inverse = np.linalg.invert(self.matrix)
        return np.dot(self.inverse, coords)


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
    source = """
        #version 120

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
        """
    function = 'LogTransform_map'
    arguments = [
        ('uniform', 'vec3', 'base'),
    ]

    def __init__(self, base=None):
        super(LogTransform, self).__init__()
        self._base = np.zeros(3, dtype=np.float32)
        self.base = (0.0, 0.0, 0.0) if base is None else base

    def map(self, coords):
        ret = np.empty(coords.shape, coords.dtype)
        base = self.base
        for i in range(ret.shape[-1]):
            if base[i] > 1.0:
                ret[..., i] = np.log(coords[..., i]) / np.log(base[i])
            else:
                ret[..., i] = coords[..., i]
        return ret

    def imap(self, coords):
        ret = np.empty(coords.shape, coords.dtype)
        base = self.base
        for i in range(ret.shape[-1]):
            if base[i] > 1.0:
                ret[..., i] = base[i] ** coords[..., i]
            else:
                ret[..., i] = coords[..., i]
        return ret

    @property
    def base(self):
        return self._base.copy()

    @base.setter
    def base(self, s):
        self._base[:len(s)] = s
        self._base[len(s):] = 0.0

    def _apply_variables(self, program):
        # Send uniforms to currently-enabled program, if any.
        program.uniforms[self._arg_map['base']] = self.base

    def __repr__(self):
        return "<LogTransform base=%s>" % (self.base)


class PolarTransform(Transform):
    pass


class BilinearTransform(Transform):
    pass


class WarpTransform(Transform):

    """ Multiple bilinear transforms in a grid arrangement.
    """
