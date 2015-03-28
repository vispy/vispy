# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import random

import numpy as np

from vispy.util.quaternion import Quaternion
from vispy.util import transforms as util_transforms
import vispy.visuals.transforms as tr
from vispy.geometry import Rect
from vispy.testing import run_tests_if_main

NT = tr.NullTransform
ST = tr.STTransform
AT = tr.AffineTransform
PT = tr.PolarTransform
LT = tr.LogTransform
CT = tr.ChainTransform


class TestDefaultTransform:

    some_translation = [
                        ('translate', (13.3, -14, 12)),
                        ('translate', (0.14, 127, -8)),
                        ('translate', (11, 0, 0)),
                        ('translate', (-117, 9, 0.5)),
                        ]
    some_scaling = [
                    ('scale', (11, 1, 1)),
                    ('scale', (10.1, 3, 7)),
                    ('scale', (11080, -10, 0.1)),
                    ('scale', (1-7, 0.01, 1)),
                    ]
    
    some_rotation = [
                     ('rotate', 130, (1, 0, 0)),
                     ('rotate', -50, (1, 2, 3)),
                     ('rotate', 140, (-1, 2, 3)),
                     ('rotate', -9, (3, -2, 30)),
                     ]
    
    def test_init(self):
        t1 = tr.DefaultTransform(scale=(1,2,3))
        t2 = tr.DefaultTransform()
        t2.scale((1,2,3))
        assert np.all(t1.get_matrix() == t2.get_matrix())
        
        q = Quaternion.create_from_axis_angle(20, 1, 2, 3)
        t1 = tr.DefaultTransform(rotate=q)
        t2 = tr.DefaultTransform()
        t2.rotate(20, (1,2,3))
        assert np.all(t1.get_matrix() == t2.get_matrix())
        
        t1 = tr.DefaultTransform(translate=(1,2,3))
        t2 = tr.DefaultTransform()
        t2.translate((1,2,3))
        assert np.all(t1.get_matrix() == t2.get_matrix())
        
        m = np.random.normal(0.0, 1.0, (4, 4))
        t1 = tr.DefaultTransform(matrix=m)
        t2 = tr.DefaultTransform()
        t2.set_matrix(m)
        assert np.all(t1.get_matrix() == t2.get_matrix())
    
    
    def test_identity(self):
        # Test that the transform is correctly identified as identity 
        
        t = tr.DefaultTransform()
        assert t.IsIdentity
        assert 'identity' in repr(t).lower()
        
        t.scale((1, 2, 4))
        assert not t.IsIdentity
        t.scale((1, 0.5, 0.25))
        assert t.IsIdentity
        
        t.translate((1, 2, 4))
        assert not t.IsIdentity
        t.translate((-1, -2, -4))
        assert t.IsIdentity
        
        t.rotate(20, (1, 2, 3))
        assert not t.IsIdentity
        t.rotate(-20, (1, 2, 3))
        #assert t.IsIdentity  # roundof errors
    
        t = tr.DefaultTransform(scale=(1,0,0))
        assert not t.IsIdentity
        
        # Setting a matrix marks it as not identity
        t = tr.DefaultTransform(matrix=np.eye(4))  # maybe we can test for eye?
        assert not t.IsIdentity
    
    def test_shear(self):
        
        # translate + scale is OK
        some_transforms = self.some_translation + self.some_scaling
        
        for iter in range(10):
            chain = [random.choice(some_transforms) for i in range(5)]
            t1 = tr.DefaultTransform()
            # Apply all transforms in the chain
            for arbitrary_transform in chain:
                f1 = getattr(t1, arbitrary_transform[0])
                f1(*arbitrary_transform[1:])
            # Check
            assert t1.IsShearless
        
        # translate + rotate is OK
        some_transforms = (self.some_rotation + self.some_translation)
        
        for iter in range(10):
            chain = [random.choice(some_transforms) for i in range(5)]
            t1 = tr.DefaultTransform()
            # Apply all transforms in the chain
            for arbitrary_transform in chain:
                f1 = getattr(t1, arbitrary_transform[0])
                f1(*arbitrary_transform[1:])
            # Check
            assert t1.IsShearless
        
        # scale + rotate is OK in that order
        t = tr.DefaultTransform()
        t.scale((1,2,3))
        t.rotate(20, (1,2,3))
        assert t.IsShearless
        
        # rotate + scale is not OK
        t = tr.DefaultTransform()
        t.rotate(20, (1,2,3))
        t.scale((1,2,3))
        assert not t.IsShearless
    
    # todo: test that linalg is not used when nonshearing
    # todo: test inversion
    
    def test_corect_composition_within_transform(self):
        # Test that DefaultTransform produces the same results as 
        # plain transform composition.
        
        some_transforms = (self.some_scaling + self.some_rotation +
                           self.some_translation)
        
        # We are going to test 10 peudo-random transform chains
        # Each consists of 5 randomly picked transforms
        for iter in range(10):
            chain = [random.choice(some_transforms) for i in range(5)]
            t1 = tr.DefaultTransform()
            t2 = np.eye(4)
            # Apply all transforms in the chain
            for arbitrary_transform in chain:
                f1 = getattr(t1, arbitrary_transform[0])
                f1(*arbitrary_transform[1:])
                f2 = getattr(util_transforms, arbitrary_transform[0])
                t2 = np.dot(t2, f2(*arbitrary_transform[1:]))
            # Check
            p1 = t1.map((1, 1, 1))
            p2 = np.dot((1, 1, 1, 1), t2)
            #print(np.isclose(p1, p2))
            assert all(np.isclose(p1, p2))
    
    def test_corect_composition_betweem_transforms(self):
        # Test that composing two DefaultTransforms yields the same
        # as having one DefaultTransform with the total chain of transforms
        
        some_transforms = (self.some_scaling + self.some_rotation +
                           self.some_translation)
                           
        # We are going to test 10 peudo-random transform chains
        # Each consists of 2*3 randomly picked transforms
        for iter in range(10):
            chain1 = [random.choice(some_transforms) for i in range(3)]
            chain2 = [random.choice(some_transforms) for i in range(3)]
            t0 = tr.DefaultTransform()
            t1 = tr.DefaultTransform()
            t2 = tr.DefaultTransform()
            # Apply all transforms in the chain
            for arbitrary_transform in chain1:
                f0 = getattr(t0, arbitrary_transform[0])
                f0(*arbitrary_transform[1:])
                f1 = getattr(t1, arbitrary_transform[0])
                f1(*arbitrary_transform[1:])
            for arbitrary_transform in chain2:
                f0 = getattr(t0, arbitrary_transform[0])
                f0(*arbitrary_transform[1:])
                f2 = getattr(t2, arbitrary_transform[0])
                f2(*arbitrary_transform[1:])
            # Check
            p0 = t0.map((1, 1, 1))
            p1 = (t1*t2).map((1, 1, 1))
            #print(np.isclose(p1, p2))
            assert all(np.isclose(p0, p1))


def assert_chain_types(chain, types):
    assert list(map(type, chain.transforms)) == types


def assert_chain_objects(chain1, chain2):
    assert chain1.transforms == chain2.transforms


def tesst_multiplication():
    n = NT()
    s = ST()
    a = AT()
    p = PT()
    l = LT()
    c1 = CT([s, a, p])
    assert c1
    c2 = CT([s, a, s])

    assert isinstance(n * n, NT)
    assert isinstance(n * s, ST)
    assert isinstance(s * s, ST)
    assert isinstance(a * s, AT)
    assert isinstance(a * a, AT)
    assert isinstance(s * a, AT)
    assert isinstance(n * p, PT)
    assert isinstance(s * p, CT)
    assert_chain_types(s * p, [PT, ST])
    assert_chain_types(s * p * a, [ST, PT, AT])
    assert_chain_types(s * a * p, [PT, AT])
    assert_chain_types(s * p * s, [ST, PT, ST])
    assert_chain_types(s * a * p * s * a, [AT, PT, AT])
    assert_chain_types(c2 * a, [AT])
    assert_chain_types(p * l * s, [ST, LT, PT])


def test_transform_chain():
    # Make dummy classes for easier distinguishing the transforms

    class DummyTrans(tr.BaseTransform):
        glsl_map = "vec4 trans(vec4 pos) {return pos;}"
        glsl_imap = "vec4 trans(vec4 pos) {return pos;}"

    class TransA(DummyTrans):
        pass

    class TransB(DummyTrans):
        pass

    class TransC(DummyTrans):
        pass

    # Create test transforms
    a, b, c = TransA(), TransB(), TransC()

    # Test Chain creation
    assert tr.ChainTransform().transforms == []
    assert tr.ChainTransform(a).transforms == [a]
    assert tr.ChainTransform(a, b).transforms == [a, b]
    assert tr.ChainTransform(a, b, c, a).transforms == [a, b, c, a]

    # Test composition by multiplication
    assert_chain_objects(a * b, tr.ChainTransform(a, b))
    assert_chain_objects(a * b * c, tr.ChainTransform(a, b, c))
    assert_chain_objects(a * b * c * a, tr.ChainTransform(a, b, c, a))

    # Test adding/prepending to transform
    chain = tr.ChainTransform()
    chain.append(a)
    assert chain.transforms == [a]
    chain.append(b)
    assert chain.transforms == [a, b]
    chain.append(c)
    assert chain.transforms == [a, b, c]
    chain.prepend(b)
    assert chain.transforms == [b, a, b, c]
    chain.prepend(c)
    assert chain.transforms == [c, b, a, b, c]

    # Test flattening
    chain1 = tr.ChainTransform(a, b)
    chain2 = tr.ChainTransform(c)
    chain3 = tr.ChainTransform(chain1, chain2)
    chain4 = tr.ChainTransform(a, b, c, chain3)
    chain5 = chain4.flat()
    assert chain5.transforms == [a, b, c, a, b, c]

    # Test simplifying
    t1 = tr.STTransform(scale=(2, 3))
    t2 = tr.STTransform(translate=(3, 4))
    t3 = tr.STTransform(translate=(3, 4))
    # Create multiplied versions
    t123 = t1*t2*t3
    t321 = t3*t2*t1
    c123 = tr.ChainTransform(t1, t2, t3)
    c321 = tr.ChainTransform(t3, t2, t1)
    c123s = c123.simplified()
    c321s = c321.simplified()
    #
    assert isinstance(t123, tr.STTransform)  # or the test is useless
    assert isinstance(t321, tr.STTransform)  # or the test is useless
    assert isinstance(c123s, tr.STTransform)  # or the test is useless
    assert isinstance(c321s, tr.STTransform)  # or the test is useless
    assert np.all(c123s.scale == t123.scale)
    assert np.all(c123s.translate == t123.translate)
    assert np.all(c321s.scale == t321.scale)
    assert np.all(c321s.translate == t321.translate)

    # Test Mapping
    t1 = tr.STTransform(scale=(2, 3))
    t2 = tr.STTransform(translate=(3, 4))
    chain1 = tr.ChainTransform(t1, t2)
    chain2 = tr.ChainTransform(t2, t1)
    #
    assert chain1.transforms == [t1, t2]  # or the test is useless
    assert chain2.transforms == [t2, t1]  # or the test is useless
    #
    m12 = (t1*t2).map((1, 1)).tolist()
    m21 = (t2*t1).map((1, 1)).tolist()
    m12_ = chain1.map((1, 1)).tolist()
    m21_ = chain2.map((1, 1)).tolist()
    #
    #print(m12, m21, m12_, m21_)
    assert m12 != m21
    assert m12 == m12_
    assert m21 == m21_

    # Test shader map
    t1 = tr.STTransform(scale=(2, 3))
    t2 = tr.STTransform(translate=(3, 4))
    chain = tr.ChainTransform(t1, t2)
    #
    funcs = chain.shader_map().dependencies()
    funcsi = chain.shader_imap().dependencies()
    #
    assert t1.shader_map() in funcs
    assert t2.shader_map() in funcs
    assert t1.shader_imap() in funcsi
    assert t2.shader_imap() in funcsi


def test_map_rect():
    r = Rect((2, 7), (13, 19))
    r1 = ST(scale=(2, 2), translate=(-10, 10)).map(r)
    assert r1 == Rect((-6, 24), (26, 38))


def test_st_mapping():
    p1 = [[5., 7.], [23., 8.]]
    p2 = [[-1.3, -1.4], [1.1, 1.2]]

    t = tr.STTransform()
    t.set_mapping(p1, p2)

    assert np.allclose(t.map(p1)[:, :len(p2)], p2)


def test_affine_mapping():
    t = tr.AffineTransform()
    p1 = np.array([[0, 0, 0],
                   [1, 0, 0],
                   [0, 1, 0],
                   [0, 0, 1]])

    # test pure translation
    p2 = p1 + 5.5
    t.set_mapping(p1, p2)
    assert np.allclose(t.map(p1)[:, :p2.shape[1]], p2)

    # test pure scaling
    p2 = p1 * 5.5
    t.set_mapping(p1, p2)
    assert np.allclose(t.map(p1)[:, :p2.shape[1]], p2)

    # test scale + translate
    p2 = (p1 * 5.5) + 3.5
    t.set_mapping(p1, p2)
    assert np.allclose(t.map(p1)[:, :p2.shape[1]], p2)

    # test SRT
    p2 = np.array([[10, 5, 3],
                   [10, 15, 3],
                   [30, 5, 3],
                   [10, 5, 3.5]])
    t.set_mapping(p1, p2)
    assert np.allclose(t.map(p1)[:, :p2.shape[1]], p2)


def test_inverse():
    m = np.random.normal(size=(4, 4))
    transforms = [
        NT(),
        ST(scale=(1e-4, 2e5), translate=(10, -6e9)),
        AT(m),
    ]

    np.random.seed(0)
    N = 20
    x = np.random.normal(size=(N, 3))
    pw = np.random.normal(size=(N, 3), scale=3)
    pos = x * 10 ** pw

    for trn in transforms:
        assert np.allclose(pos, trn.inverse.map(trn.map(pos))[:, :3])

    # log transform only works on positive values
    #abs_pos = np.abs(pos)
    #tr = LT(base=(2, 4.5, 0))
    #assert np.allclose(abs_pos, tr.inverse.map(tr.map(abs_pos))[:,:3])


run_tests_if_main()
