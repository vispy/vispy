import vispy.scene.transforms as tr
import numpy as np

NT = tr.NullTransform
ST = tr.STTransform
AT = tr.AffineTransform
PT = tr.PolarTransform
LT = tr.LogTransform
CT = tr.ChainTransform


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
    
    class DummyTrans(tr.Transform):
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
    chain4.flatten()
    assert chain4.transforms == [a, b, c, a, b, c]

    # Test simplifying
    t1 = tr.STTransform(scale=(2, 3))
    t2 = tr.STTransform(translate=(3, 4))
    t3 = tr.STTransform(translate=(3, 4))
    # Create multiplied versions
    t123 = t1*t2*t3
    t321 = t3*t2*t1
    c123 = tr.ChainTransform(t1, t2, t3)
    c321 = tr.ChainTransform(t3, t2, t1)
    c123.simplify()
    c321.simplify()
    #
    assert isinstance(t123, tr.STTransform)  # or the test is useless
    assert isinstance(t321, tr.STTransform)  # or the test is useless
    assert len(c123.transforms) == 1
    assert len(c321.transforms) == 1
    assert np.all(c123.transforms[0].scale == t123.scale)
    assert np.all(c123.transforms[0].translate == t123.translate)
    assert np.all(c321.transforms[0].scale == t321.scale)
    assert np.all(c321.transforms[0].translate == t321.translate)

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
    from vispy.util.geometry import Rect
    r = Rect((2, 7), (13, 19))
    r1 = ST(scale=(2, 2), translate=(-10, 10)).map(r)
    assert r1 == Rect((-6, 24), (26, 38))


if __name__ == '__main__':
    for key in [key for key in globals()]:
        if key.startswith('test_'):
            func = globals()[key]
            print('running', func.__name__)
            func()
