# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
A collection is a container for several items having the same data
structure (dtype). Each data type can be declared as local (it specific to a
vertex), shared (it is shared among an item vertices) or global (it is shared
by all vertices). It is based on the BaseCollection but offers a more intuitive
interface.
"""

import numpy as np
from ... import gloo
from . util import fetchcode
from . base_collection import BaseCollection
from ..shaders import ModularProgram
from ...util.event import EventEmitter


class Collection(BaseCollection):

    """
    A collection is a container for several items having the same data
    structure (dtype). Each data type can be declared as local (it is specific
    to a vertex), shared (it is shared among item vertices) or global (it is
    shared by all items). It is based on the BaseCollection but offers a more
    intuitive interface.

    Parameters
    ----------

    dtype: list
        Data individual types as (name, dtype, scope, default)

    itype: np.dtype or None
        Indices data type

    mode : GL_ENUM
        GL_POINTS, GL_LINES, GL_LINE_STRIP, GL_LINE_LOOP,
        GL_TRIANGLES, GL_TRIANGLE_STRIP, GL_TRIANGLE_FAN

    vertex: str or tuple of str
       Vertex shader to use to draw this collection

    fragment:  str or tuple of str
       Fragment shader to use to draw this collection

    kwargs: str
        Scope can also be specified using keyword argument,
        where parameter name must be one of the dtype.
    """

    _gtypes = {('float32', 1): "float",
               ('float32', 2): "vec2",
               ('float32', 3): "vec3",
               ('float32', 4): "vec4",
               ('int32', 1): "int",
               ('int32', 2): "ivec2",
               ('int32', 3): "ivec3",
               ('int32', 4): "ivec4"}

    def __init__(self, dtype, itype, mode, vertex, fragment, program=None, 
                 **kwargs):
        """
        """

        self._uniforms = {}
        self._attributes = {}
        self._varyings = {}
        self._mode = mode
        vtype = []
        utype = []
        
        self.update = EventEmitter(source=self, type='collection_update')

        # Build vtype and utype according to parameters
        declarations = {"uniforms": "",
                        "attributes": "",
                        "varyings": ""}
        defaults = {}
        for item in dtype:
            name, (basetype, count), scope, default = item
            basetype = np.dtype(basetype).name
            if scope[0] == "!":
                scope = scope[1:]
            else:
                scope = kwargs.pop(name, scope)
            defaults[name] = default
            gtype = Collection._gtypes[(basetype, count)]
            if scope == "local":
                vtype.append((name, basetype, count))
                declarations[
                    "attributes"] += "attribute %s %s;\n" % (gtype, name)
            elif scope == "shared":
                utype.append((name, basetype, count))
                declarations["varyings"] += "varying %s %s;\n" % (gtype, name)
            else:
                declarations["uniforms"] += "uniform %s %s;\n" % (gtype, name)
                self._uniforms[name] = None

        if len(kwargs) > 0:
            raise NameError("Invalid keyword argument(s): %s" % 
                            list(kwargs.keys()))
        
        vtype = np.dtype(vtype)
        itype = np.dtype(itype) if itype else None
        utype = np.dtype(utype) if utype else None

        BaseCollection.__init__(self, vtype=vtype, utype=utype, itype=itype)
        self._declarations = declarations
        self._defaults = defaults

        # Build program (once base collection is built)
        saved = vertex
        vertex = ""

        if self.utype is not None:
            vertex += fetchcode(self.utype) + vertex
        else:
            vertex += "void fetch_uniforms(void) { }\n" + vertex
        vertex += self._declarations["uniforms"]
        vertex += self._declarations["attributes"]
        vertex += saved

        self._vertex = vertex
        self._fragment = fragment

        if program is None:
            program = ModularProgram(vertex, fragment)
        else:
            program.vert = vertex
            program.frag = fragment
        if hasattr(program, 'changed'):
            program.changed.connect(self.update)
        self._programs.append(program)

        # Initialize uniforms
        for name in self._uniforms.keys():
            self._uniforms[name] = self._defaults.get(name)
            program[name] = self._uniforms[name]

    def view(self, transform, viewport=None):
        """ Return a view on the collection using provided transform """

        return CollectionView(self, transform, viewport)

        # program = gloo.Program(self._vertex, self._fragment)
        # if "transform" in program.hooks:
        #     program["transform"] = transform
        # if "viewport" in program.hooks:
        #     if viewport is not None:
        #         program["viewport"] = viewport
        #     else:
        #         program["viewport"] = Viewport()
        # self._programs.append(program)
        # program.bind(self._vertices_buffer)
        # for name in self._uniforms.keys():
        #     program[name] = self._uniforms[name]
        # #if self._uniforms_list is not None:
        # #    program["uniforms"] = self._uniforms_texture
        # #    program["uniforms_shape"] = self._ushape

        # # Piggy backing
        # def draw():
        #     if self._need_update:
        #         self._update()
        #         program.bind(self._vertices_buffer)
        #         if self._uniforms_list is not None:
        #             program["uniforms"] = self._uniforms_texture
        #             program["uniforms_shape"] = self._ushape

        #     if self._indices_list is not None:
        #         Program.draw(program, self._mode, self._indices_buffer)
        #     else:
        #         Program.draw(program, self._mode)

        # program.draw = draw
        # return program

    def __getitem__(self, key):

        program = self._programs[0]
        for name, (storage, _, _) in program._code_variables.items():
            if name == key and storage == 'uniform':
                return program[key]
        return BaseCollection.__getitem__(self, key)

    def __setitem__(self, key, value):
        try:
            BaseCollection.__setitem__(self, key, value)
        except IndexError:
            for program in self._programs:
                program[key] = value

    def draw(self, mode=None):
        """ Draw collection """

        if self._need_update:
            self._update()

        program = self._programs[0]

        mode = mode or self._mode
        if self._indices_list is not None:
            program.draw(mode, self._indices_buffer)
        else:
            program.draw(mode)


class CollectionView(object):

    def __init__(self, collection, transform=None, viewport=None):

        vertex = collection._vertex
        fragment = collection._fragment
        program = gloo.Program(vertex, fragment)

#        if "transform" in program.hooks and transform is not None:
#            program["transform"] = transform
#        if "viewport" in program.hooks and viewport is not None:
#            program["viewport"] = viewport

        program.bind(collection._vertices_buffer)
        for name in collection._uniforms.keys():
            program[name] = collection._uniforms[name]

        collection._programs.append(program)
        self._program = program
        self._collection = collection

    def __getitem__(self, key):
        return self._program[key]

    def __setitem__(self, key, value):
        self._program[key] = value

    def draw(self):

        program = self._program
        collection = self._collection
        mode = collection._mode

        if collection._need_update:
            collection._update()
            # self._program.bind(self._vertices_buffer)
            if collection._uniforms_list is not None:
                program["uniforms"] = collection._uniforms_texture
                program["uniforms_shape"] = collection._ushape

        if collection._indices_list is not None:
            program.draw(mode, collection._indices_buffer)
        else:
            program.draw(mode)
