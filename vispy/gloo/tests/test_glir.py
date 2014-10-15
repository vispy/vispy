# -*- coding: utf-8 -*-

from vispy.gloo import glir

from vispy.testing import run_tests_if_main


def test__queue():
    q = glir.GlirQueue()
    
    # Test adding commands and clear
    N = 5
    for i in range(N):
        q.command('FOO', 'BAR', i)
    cmds = q.clear()
    for i in range(N):
        assert cmds[i] == ('FOO', 'BAR', i)
    
    # Test filter 1
    cmds1 = [('DATA', 1), ('SIZE', 1), ('FOO', 1), ('SIZE', 1), ('FOO', 1), 
             ('DATA', 1), ('DATA', 1)]
    cmds2 = [c[0] for c in q._filter(cmds1)]
    assert cmds2 == ['FOO', 'SIZE', 'FOO', 'DATA', 'DATA']
    
    # Test filter 2
    cmds1 = [('DATA', 1), ('SIZE', 1), ('FOO', 1), ('SIZE', 2), ('SIZE', 2), 
             ('DATA', 2), ('SIZE', 1), ('FOO', 1), ('DATA', 1), ('DATA', 1)]
    cmds2 = q._filter(cmds1)
    assert cmds2 == [('FOO', 1), ('SIZE', 2), ('DATA', 2), ('SIZE', 1), 
                     ('FOO', 1), ('DATA', 1), ('DATA', 1)]


# The rest is basically tested via our examples
    
run_tests_if_main()
