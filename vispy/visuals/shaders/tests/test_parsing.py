# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import re

from vispy.visuals.shaders.parsing import re_identifier, find_program_variables
from vispy.testing import run_tests_if_main


def test_identifier():
    assert(re.match('('+re_identifier+')', 'Ax2_d3__7').groups()[0] ==
           'Ax2_d3__7')
    assert(re.match('('+re_identifier+')', '_Ax2_d3__7').groups()[0] ==
           '_Ax2_d3__7')
    assert(re.match(re_identifier, '7Ax2_d3__7') is None)
    assert(re.match('('+re_identifier+')', 'x,y').groups()[0] == 'x')
    assert(re.match('('+re_identifier+')', 'x y').groups()[0] == 'x')


def test_find_variables():
    code = """
    float x;
    float y, z;
    int w,v,u;
    junk
    vec4 t = vec4(0, 0, 1, 1);
    junk junk junk;
    uniform vec2 s;
    attribute float r,q;
    const mat4 p;
    void main() {
        vec2 float undetectable;
    }
    """
    
    expect = dict(
        x=(None, 'float'),
        y=(None, 'float'),
        z=(None, 'float'),
        w=(None, 'int'),
        v=(None, 'int'),
        u=(None, 'int'),
        t=(None, 'vec4'),
        s=('uniform', 'vec2'),
        q=('attribute', 'float'),
        r=('attribute', 'float'),
        p=('const', 'mat4'),
    )

    vars = find_program_variables(code)
    for k in expect:
        assert expect[k] == vars.pop(k)
        
    assert len(vars) == 0


run_tests_if_main()
