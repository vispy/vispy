#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2013, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------

import numpy as np
from functools import reduce
from operator import mul


def dtype_reduce(dtype, level=0, depth=0):
    """
    Try to reduce dtype up to a given level when it is possible

    dtype =  [ ('vertex',  [('x', 'f4'), ('y', 'f4'), ('z', 'f4')]),
               ('normal',  [('x', 'f4'), ('y', 'f4'), ('z', 'f4')]),
               ('color',   [('r', 'f4'), ('g', 'f4'), ('b', 'f4'),
                            ('a', 'f4')])]

    level 0: ['color,vertex,normal,', 10, 'float32']
    level 1: [['color', 4, 'float32']
              ['normal', 3, 'float32']
              ['vertex', 3, 'float32']]
    """
    dtype = np.dtype(dtype)
    fields = dtype.fields

    # No fields
    if fields is None:
        if len(dtype.shape):
            count = reduce(mul, dtype.shape)
        else:
            count = 1
        # size = dtype.itemsize / count
        if dtype.subdtype:
            name = str(dtype.subdtype[0])
        else:
            name = str(dtype)
        return ['', count, name]
    else:
        items = []
        name = ''
        # Get reduced fields
        for key, value in fields.items():
            l = dtype_reduce(value[0], level, depth + 1)
            if type(l[0]) is str:
                items.append([key, l[1], l[2]])
            else:
                items.append(l)
            name += key + ','

        # Check if we can reduce item list
        ctype = None
        count = 0
        for i, item in enumerate(items):
            # One item is a list, we cannot reduce
            if type(item[0]) is not str:
                return items
            else:
                if i == 0:
                    ctype = item[2]
                    count += item[1]
                else:
                    if item[2] != ctype:
                        return items
                    count += item[1]
        if depth >= level:
            return [name, count, ctype]
        else:
            return items


def fetchcode(utype, prefix=""):
    """
    Generate the GLSL code needed to retrieve fake uniform values from a
    texture.

    uniforms : sampler2D
        Texture to fetch uniforms from

    uniforms_shape: vec3
        Size of texture (width,height,count) where count is the number of float
        to be fetched.

    collection_index: float
        Attribute giving the index of the uniforms to be fetched. This index
       relates to the index in the uniform array from python side.
    """

    utype = np.dtype(utype)
    _utype = dtype_reduce(utype, level=1)

    header = """
uniform   sampler2D uniforms;
uniform   vec3      uniforms_shape;
attribute float     collection_index;

"""

    # Header generation (easy)
    types = {1: 'float', 2: 'vec2 ', 3: 'vec3 ',
             4: 'vec4 ', 9: 'mat3 ', 16: 'mat4 '}
    for name, count, _ in _utype:
        if name != '__unused__':
            header += "varying %s %s%s;\n" % (types[count], prefix, name)

    # Body generation (not so easy)
    body = """\nvoid fetch_uniforms() {
    float rows   = uniforms_shape.x;
    float cols   = uniforms_shape.y;
    float count  = uniforms_shape.z;
    float index  = collection_index;
    int index_x  = int(mod(index, (floor(cols/(count/4.0))))) * int(count/4.0);
    int index_y  = int(floor(index / (floor(cols/(count/4.0)))));
    float size_x = cols - 1.0;
    float size_y = rows - 1.0;
    float ty     = 0.0;
    if (size_y > 0.0)
        ty = float(index_y)/size_y;
    int i = index_x;
    vec4 _uniform;\n"""

    _utype = dict([(name, count) for name, count, _ in _utype])
    store = 0
    # Be very careful with utype name order (_utype.keys is wrong)
    for name in utype.names:
        if name == '__unused__':
            continue
        count, shift = _utype[name], 0
        size = count
        while count:
            if store == 0:
                body += "\n    _uniform = texture2D(uniforms, vec2(float(i++)/size_x,ty));\n"  # noqa
                store = 4
            if store == 4:
                a = "xyzw"
            elif store == 3:
                a = "yzw"
            elif store == 2:
                a = "zw"
            elif store == 1:
                a = "w"
            if shift == 0:
                b = "xyzw"
            elif shift == 1:
                b = "yzw"
            elif shift == 2:
                b = "zw"
            elif shift == 3:
                b = "w"
            i = min(min(len(b), count), len(a))
            if size > 1:
                body += "    %s%s.%s = _uniform.%s;\n" % (prefix, name, b[:i], a[:i])  # noqa
            else:
                body += "    %s%s = _uniform.%s;\n" % (prefix, name, a[:i])
            count -= i
            shift += i
            store -= i

    body += """}\n\n"""
    return header + body
