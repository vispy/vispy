from nose.tools import assert_raises

from vispy.scene.shaders.function import Function, Variable


def test_function():
    func = Function("""
    vec3 my_function(vec2 x, float z) {
        return vec3(vec2, z);
    }
    """)

    assert(func.name == 'my_function')
    assert(func.rtype == 'vec3')
    assert(func.args == [('vec2', 'x'), ('float', 'z')])
    assert(not func.is_anonymous)

    func.compile({})  # ok
    func.compile({func: 'my_function'})  # ok
    assert_raises(Exception, lambda: func.compile({func: 'wrong_name'}))

    func2 = Function("""
    vec3 $my_function2() {
        return vec3($xy, $z);
    }
    """)

    assert(func2.name == 'my_function2')
    assert(func2.rtype == 'vec3')
    assert(func2.args == [])
    assert(func2.is_anonymous)
    assert('xy' in func2.template_vars)
    assert('z' in func2.template_vars)

    func2['xy'] = ('varying', 'vec2')
    func2['z'] = ('varying', 'float')

    # raise exception because xy and z are not specified in compile
    assert_raises(Exception, lambda: func2.compile({func2: 'func_name'}))

    assert(isinstance(func2['xy'], Variable))
    assert(func2['xy'].vtype == 'varying')
    assert(func2['xy'].dtype == 'vec2')
    assert(func2['xy'].is_anonymous)
    assert(func2['xy'].compile({}) == 'varying vec2 xy;')
    assert(func2['z'].compile({}) == 'varying float z;')
    assert(func2['xy'].compile({func2['xy']: 'vname'}) ==
           'varying vec2 vname;')

    names = {func2: 'some_function', func2['xy']: 'var_xy',
             func2['z']: 'var_z'}
    func3 = Function(func2.compile(names))
    assert(func3.name == 'some_function')


#vmain = """
#vec3 my_hook1(vec2 x, float y);
#vec3 my_hook2(vec2 x);
#vec4 my_hook3(vec4 x);

#void main() {

#}

#"""

#fmain = """
#void main() {

#}
#"""

#prog = CompositeProgram(vmain, fmain)

#assert_raises(NameError, lambda: prog.set_hook('my_hookX', func))
#assert_raises(TypeError, lambda: prog.set_hook('my_hook2', func))

#prog.set_hook('my_hook1', func)
#bound = func2.bind('my_hook2', z=('uniform', 'float', 'u_input_z'))

#assert(bound.name == 'my_hook2')
#assert(bound.args == [('vec2', 'x')])
#assert(bound.rtype == 'vec3')

#prog.set_hook('my_hook2', bound)


#fn1 = ShaderFunction("""
#vec4 fn1(vec4 x) {
    #return x;
#}
#""")

#fn2 = ShaderFunction("""
#vec4 fn2(vec4 x) {
    #return x;
#}
#""")

#fn3 = ShaderFunction("""
#vec4 fn3(vec4 x) {
    #return x;
#}
#""")


#chain = ShaderFunctionChain('my_hook3', [fn1, fn2, fn3])
#prog.set_hook('my_hook3', chain)

#print "\n".join(prog.generate_code())
