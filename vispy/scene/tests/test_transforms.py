import vispy.visuals.transforms as tr

NT = tr.NullTransform
ST = tr.STTransform
AT = tr.AffineTransform
PT = tr.PolarTransform
LT = tr.LogTransform
CT = tr.ChainTransform

def assert_chain_types(chain, types):
    assert map(type, chain.transforms) == types

def test_multiplication():
    n = NT()
    s = ST()
    a = AT()
    p = PT()
    l = LT()
    c1 = CT([s, a, p])
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
    assert_chain_types(s * p * a, [AT, PT, ST])
    assert_chain_types(s * a * p, [PT, AT])
    assert_chain_types(s * p * s, [ST, PT, ST])
    assert_chain_types(s * a * p * s * a, [AT, PT, AT])
    assert_chain_types(c2 * a, [AT])
    assert_chain_types(p * l * s, [ST, LT, PT])
    
def test_map_rect():
    from vispy.util.geometry import Rect
    r = Rect((2, 7), (13, 19))
    r1 = ST(scale=(2, 2), translate=(-10, 10)).map(r)
    assert r1 == Rect((-6, 24), (26, 38))


