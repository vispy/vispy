# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ..shaders import FunctionChain
from .base_transform import BaseTransform
from .linear import NullTransform


class ChainTransform(BaseTransform):
    """
    BaseTransform subclass that performs a sequence of transformations in
    order. Internally, this class uses shaders.FunctionChain to generate
    its glsl_map and glsl_imap functions.

    Arguments:

    transforms : list of BaseTransform instances
    """
    glsl_map = None
    glsl_imap = None

    Linear = False
    Orthogonal = False
    NonScaling = False
    Isometric = False

    def __init__(self, *transforms):
        super(ChainTransform, self).__init__()

        # Set input transforms
        trs = []
        for tr in transforms:
            if isinstance(tr, (tuple, list)):
                trs.extend(tr)
            else:
                trs.append(tr)
        self._transforms = trs

        # Post-process
        self.flatten()
        #if simplify:
        #    self.simplify()

        # ChainTransform does not have shader maps
        self._shader_map = None
        self._shader_imap = None

    @property
    def transforms(self):
        """ Get the list of transform that make up the transform chain.
        """
        return self._transforms

#     @transforms.setter
#     def transforms(self, tr):
#         #if self._enabled:
#             #raise RuntimeError("Shader is already enabled; cannot modify.")
#         if not isinstance(tr, list):
#             raise TypeError("Transform chain must be a list")
#         self._transforms = tr

    @property
    def Linear(self):
        b = True
        for tr in self._transforms:
            b &= tr.Linear
        return b

    @property
    def Orthogonal(self):
        b = True
        for tr in self._transforms:
            b &= tr.Orthogonal
        return b

    @property
    def NonScaling(self):
        b = True
        for tr in self._transforms:
            b &= tr.NonScaling
        return b

    @property
    def Isometric(self):
        b = True
        for tr in self._transforms:
            b &= tr.Isometric
        return b

    def map(self, obj):
        for tr in reversed(self.transforms):
            obj = tr.map(obj)
        return obj

    def imap(self, obj):
        for tr in self.transforms:
            obj = tr.imap(obj)
        return obj

    def shader_map(self):
        if self._shader_map is None:
            self._shader_map = self._make_shader_map(imap=False)
        else:
            for tr in self._transforms:
                tr.shader_map()  # force transform to update its shader
        return self._shader_map

    def shader_imap(self):
        if self._shader_imap is None:
            self._shader_imap = self._make_shader_map(imap=True)
        else:
            for tr in self._transforms:
                tr.shader_imap()  # force transform to update its shader
        return self._shader_imap

    def _make_shader_map(self, imap):
        if imap is True:
            funcs = [tr.shader_imap() for tr in self.transforms]
        else:
            funcs = [tr.shader_map() for tr in reversed(self.transforms)]

        #bindings = []
        #for i,tr in enumerate(transforms):

            #tr_name = '%s_%d_%s' % (name, i, type(tr).__name__)
            #if imap:
            #    bound = tr.shader_imap(tr_name)
            #else:
            #    bound = tr.shader_map(tr_name)
            #bindings.append(bound)

        name = "transform_%s_chain" % ('imap' if imap is not None else 'map')
        return FunctionChain(name, funcs)

    def inverse(self):
        return ChainTransform([tr.inverse()
                               for tr in reversed(self.transforms)])

    def flatten(self):
        """
        Attempt to simplify the chain by expanding any nested chains.
        """
        # Flatten untill there is nothing more to flatten
        encountered_chains = True
        while encountered_chains:
            encountered_chains = False
            #
            new_tr = []
            for tr in self.transforms:
                if isinstance(tr, ChainTransform):
                    encountered_chains = True
                    new_tr.extend(tr.transforms)
                else:
                    new_tr.append(tr)
            self._transforms = new_tr

    def simplify(self):
        """
        Attempt to simplify the chain by joining adjacent transforms.
        If the result is a single transform, return that transform.
        Otherwise return this chaintransform.
        """
        self.flatten()
        if len(self.transforms) == 0:
            return NullTransform()
        cont = True
        while cont:
            new_tr = [self.transforms[0]]
            cont = False
            for t2 in self.transforms[1:]:
                t1 = new_tr[-1]
                pr = t1 * t2
                if not isinstance(pr, ChainTransform):
                    cont = True
                    new_tr.pop()
                    new_tr.append(pr)
                else:
                    new_tr.append(t2)
            self._transforms = new_tr

        # todo: get rid of this in-place + return thing
        if len(self._transforms) == 1:
            return self._transforms[0]
        else:
            return self

    def append(self, tr):
        """
        Add a new transform to the end of this chain.
        """
        self.transforms.append(tr)
        # Keep simple for now. Let's look at efficienty later
        # I feel that this class should not decide when to compose transforms
#         while len(self.transforms) > 0:
#             pr = tr * self.transforms[-1]
#             if isinstance(pr, ChainTransform):
#                 self.transforms.append(tr)
#                 break
#             else:
#                 self.transforms.pop()
#                 tr = pr
#                 if len(self.transforms)  == 0:
#                     self._transforms = [pr]
#                     break

    def prepend(self, tr):
        """
        Add a new transform to the beginning of this chain.
        """
        self.transforms.insert(0, tr)
        # Keep simple for now. Let's look at efficienty later
#         while len(self.transforms) > 0:
#             pr = self.transforms[0] * tr
#             if isinstance(pr, ChainTransform):
#                 self.transforms.insert(0, tr)
#                 break
#             else:
#                 self.transforms.pop(0)
#                 tr = pr
#                 if len(self.transforms)  == 0:
#                     self._transforms = [pr]
#                     break

    def __mul__(self, tr):
        if isinstance(tr, ChainTransform):
            trs = tr.transforms
        else:
            trs = [tr]
        return ChainTransform(self.transforms+trs)

    def __rmul__(self, tr):
        if isinstance(tr, ChainTransform):
            trs = tr.transforms
        else:
            trs = [tr]
        return ChainTransform(trs+self.transforms)

    def __repr__(self):
        names = [tr.__class__.__name__ for tr in self.transforms]
        return "<ChainTransform [%s]>" % (", ".join(names))
