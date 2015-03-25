from vispy.scene.node import Node
from vispy.testing import run_tests_if_main


def test_graph():
    # Graph looks like:
    # 
    #  a --- b --- c --- d --- g
    #         \            /
    #          --- e --- f 
    #
    a = Node(name='a')
    b = Node(name='b', parent=a)
    c = Node(name='c', parent=b)
    d = Node(name='d', parent=c)
    e = Node(name='e', parent=b)
    f = Node(name='f', parent=e)
    g = Node(name='g', )
    g.parents = (f, d)
    
    assert a.parent is None
    assert b.node_path(a) == ([b, a], [])
    assert a.node_path(b) == ([a], [b])
    assert c.node_path(a) == ([c, b, a], [])
    assert a.node_path(c) == ([a], [b, c])
    assert d.node_path(f) == ([d, c, b], [e, f])
    assert f.node_path(d) == ([f, e, b], [c, d])
    try:
        g.node_path(b)
        raise Exception("Should have raised RuntimeError")
    except RuntimeError:
        pass


run_tests_if_main()
