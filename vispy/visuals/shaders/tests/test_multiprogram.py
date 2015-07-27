# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
from vispy.visuals.shaders import MultiProgram, Function, StatementList
from vispy.visuals.transforms import STTransform, MatrixTransform


def test_multiprogram():
    vert = """
    uniform float u_scale;
    
    void main() {
        gl_Position = $transform(vec4(0, 0, 0, 0));
    }
    """
    
    frag = """
    void main() {
        gl_FragColor = $color;
        $post_hook
    }
    """
    
    # test adding programs
    mp = MultiProgram(vert, frag)
    p1 = mp.add_program()
    p2 = mp.add_program('p2')
    assert 'p2' in mp._programs
    
    # test weak reference to program
    mp.add_program('junk')
    assert 'junk' not in mp._programs and len(mp._programs) == 2

    # test setting variables on multiprogram or individual programs
    mp['u_scale'] = 2
    assert p1['u_scale'] == 2
    assert p2['u_scale'] == 2
    
    p1['u_scale'] = 3
    assert p1['u_scale'] == 3
    assert p2['u_scale'] == 2
    
    # test setting template variables globally
    mp.frag['color'] = (1, 1, 1, 1)
    assert p1.frag['color'].value == (1, 1, 1, 1)
    assert p2.frag['color'].value == (1, 1, 1, 1)
    
    # test setting template variables per-program
    func = Function("""
    void filter() {
        gl_FragColor.r = 0.5;
    }
    """)
    p1.frag['post_hook'] = StatementList()
    p2.frag['post_hook'] = StatementList()
    p2.frag['post_hook'].add(func())
    
    tr1 = STTransform()
    tr2 = MatrixTransform()
    p1.vert['transform'] = tr1
    p2.vert['transform'] = tr2
    
    assert 'st_transform_map' in p1.vert.compile()
    assert 'affine_transform_map' in p2.vert.compile()
    assert 'filter' not in p1.frag.compile()
    assert 'filter' in p2.frag.compile()
    
    # test changing shader code
    mp.vert = vert + '\n//test\n'
    mp.vert['transform'] = tr1
    assert '//test' in p1.vert.compile()
    
    # test that newly-added programs inherit all previously set variables
    p3 = mp.add_program()
    assert p3['u_scale'] == 2
    assert p3.frag['color'].value == (1, 1, 1, 1)
    assert '//test' in p3.vert.compile()
    assert 'st_transform_map' in p3.vert.compile()
