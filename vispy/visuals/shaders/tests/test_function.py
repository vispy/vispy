# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
from vispy.visuals.shaders import (Function, MainFunction, Variable, Varying,
                                   FunctionChain, StatementList)


# Users normally don't need these, but I want to test them
from vispy.visuals.shaders.expression import FunctionCall, TextExpression

from vispy.testing import (assert_in, assert_not_in, assert_is,
                           run_tests_if_main, assert_raises, assert_equal)


# Define some snippets

transformScale = Function("""
vec4 transform_scale(vec4 pos)
{
    pos.xyz *= $scale;
    return pos;
}
""")

transformZOffset = Function("""
vec4 transform_zoffset(vec4 pos)
{
    pos.z += $offset;
    return pos;
}
""")

vert_template = Function("""
void main(void)
{   
    int nlights = $nlights;
    vec4 pos = $position;
    pos += $correction;
    gl_Position = $endtransform(pos);
}

""")

frag_template = Function("""
void main(void)
{
    gl_Fragcolor = $color;
}

""")

data = 'just some dummy variable, Function is agnostic about this'


# Examples

def test_example1():
    """Just a few simple compositions."""
    # Get function objects. Generate random name for transforms
    code = Function(vert_template)
    t1 = Function(transformScale)
    t2 = Function(transformZOffset)
    t3 = Function(transformScale)

    # We need to create a variable in order to use it in two places
    pos = Variable('attribute vec4 a_position')

    # Compose everything together
    code['position'] = t1(t2(pos))
    code['correction'] = t1(pos)  # Look, we use t1 again, different sig
    code['endtransform'] = t3  # function pointer rather than function call
    code['nlights'] = '4'
    t1['scale'] = t2
    t3['scale'] = (3.0, 4.0, 5.0)
    t2['offset'] = '1.0'

    code2 = Function(frag_template)
    code2['color'] = Varying('v_position')

    code['gl_PointSize'] = '3.0'
    code[code2['color']] = pos
    print(code)


def test_example2():
    """Demonstrate how a transform would work."""
    vert_template = Function("""
    void main(void)
    {
        gl_Position = $position;
    }
    """)

    transformScale = Function("""
    vec4 transform_scale(vec4 pos)
    {
        pos.xyz *= $scale;
        return pos;
    }
    """)

    class Transform(object):
        def __init__(self):
            # Equivalent methods to create new function object
            self.func = Function(transformScale)
            self.func['scale'] = 'uniform float'
            # self.func = Function(transformScale)

        def set_scale(self, scale):
            self.func['scale'].value = scale

    transforms = [Transform(), Transform(), Transform()]

    code = Function(vert_template)
    ob = Variable('attribute vec3 a_position')
    for trans in transforms:
        ob = trans.func(ob)
    code['position'] = ob
    print(code)

# Tests


def test_TextExpression():
    exp = TextExpression('foo bar')
    assert_equal('foo bar', exp.expression(None))
    assert_equal(None, exp.definition(None, ('120', '')))
    assert_raises(TypeError, TextExpression, 4)


def test_FunctionCall():
    fun = Function(transformScale)
    fun['scale'] = '1.0'
    fun2 = Function(transformZOffset)

    # No args
    assert_raises(TypeError, fun)  # need 1 arg
    assert_raises(TypeError, fun, 1, 2)  # need 1 arg
    call = fun('x')
    # Test repr
    exp = call.expression({fun: 'y'})
    assert_equal(exp, 'y(x)')
    # Test sig
    assert len(call._args) == 1
    # Test dependencies
    assert_in(fun, call.dependencies())
    assert_in(call._args[0], call.dependencies())

    # More args
    call = fun(fun2('foo'))
    # Test repr
    exp = call.expression({fun: 'y', fun2: 'z'})
    assert_in('y(z(', exp)
    # Test sig
    assert len(call._args) == 1
    call2 = call._args[0]
    assert len(call2._args) == 1
    # Test dependencies
    assert_in(fun, call.dependencies())
    assert_in(call._args[0], call.dependencies())
    assert_in(fun2, call.dependencies())
    assert_in(call2._args[0], call.dependencies())


def test_Variable():

    # Test init fail
    assert_raises(TypeError, Variable)  # no args
    assert_raises(TypeError, Variable, 3)  # wrong type
    assert_raises(TypeError, Variable, "name", "str")  # wrong type
    assert_raises(ValueError, Variable, 'bla bla')  # need correct vtype
    assert_raises(ValueError, Variable, 'uniform b l a')  # too many

    # Test init success
    var = Variable('uniform float bla')  # Finally
    assert_equal(var.name, 'bla')
    assert_equal(var.dtype, 'float')
    assert_equal(var.vtype, 'uniform')
    assert var.value is None

    # test assign new value
    var.value = 10.
    assert_equal(var.dtype, 'float')  # type is locked; won't change

    # test name-only init
    var = Variable('bla')  # Finally
    assert_equal(var.name, 'bla')
    assert_equal(var.dtype, None)
    assert_equal(var.vtype, None)
    assert var.value is None

    # test assign new value
    var.value = 10
    assert_equal(var.dtype, 'int')
    assert_equal(var.vtype, 'uniform')
    assert_equal(var.value, 10)

    # test init with value
    var = Variable('bla', (1, 2, 3))  # Also valid
    assert_equal(var.name, 'bla')
    assert_equal(var.dtype, 'vec3')
    assert_equal(var.vtype, 'uniform')
    assert_equal(var.value, (1, 2, 3))

    # Test value
    # var = Variable('uniform float bla', data)  # Also valid
    # assert_equal(var.value, data)
    # var.value = 3
    # assert_equal(var.value, 3)

    # Test repr
    var = Variable('uniform float bla')
    assert_in('uniform float bla', var.compile())

    # Test injection, definition, dependencies
    assert_equal(var.expression({var: 'xxx'}), 'xxx')
    assert_equal(var.definition({var: 'xxx'}, ('120', ''), None),
                 'uniform float xxx;')
    assert_in(var, var.dependencies())

    # Renaming
    var = Variable('uniform float bla')
    assert_equal(var.name, 'bla')
    var.name = 'foo'
    assert_equal(var.name, 'foo')


def test_function_basics():

    # Test init fail
    assert_raises(TypeError, Function)  # no args
    assert_raises(ValueError, Function, 3)  # need string

    # Test init success 1
    fun = Function('void main(){}')
    assert_equal(fun.name, 'main')
    assert len(fun.template_vars) == 0

    # Test init success with template vars
    fun = Function('void main(){$foo; $bar;}')
    assert_equal(fun.name, 'main')
    assert len(fun.template_vars) == 2
    assert_in('foo', fun.template_vars)

    # Test that `var in fun` syntax works as well
    assert 'foo' in fun
    assert 'bar' in fun
    assert 'baz' not in fun

    assert_in('bar', fun.template_vars)

    # Test setting verbatim expressions
    assert_raises(KeyError, fun.__setitem__, 'bla', '33')  # no such template
    fun['foo'] = '33'
    fun['bar'] = 'bla bla'
    assert_is(type(fun['foo']), TextExpression)
    assert_equal(fun['foo'].expression(None), '33')
    assert_is(type(fun['bar']), TextExpression)
    assert_equal(fun['bar'].expression(None), 'bla bla')

    # Test setting call expressions
    fun = Function('void main(){\n$foo;\n$bar;\n$spam(XX);\n$eggs(YY);\n}')
    trans = Function('float transform_scale(float x) {return x+1.0;}')
    assert_raises(TypeError, trans)  # requires 1 arg 
    assert_raises(TypeError, trans, '1', '2')
    fun['foo'] = trans('2')
    fun['bar'] = trans('3')
    fun['spam'] = trans
    fun['eggs'] = trans
    #
    for name in ['foo', 'bar']:
        assert_is(type(fun[name]), FunctionCall)
        assert_equal(fun[name].function, trans)
        assert_in(trans, fun.dependencies())
    for name in ['spam', 'eggs']:
        assert_equal(fun[name], trans)

    #
    text = fun.compile()
    assert_in('\ntransform_scale(2);\n', text)
    assert_in('\ntransform_scale(3);\n', text)
    assert_in('\ntransform_scale(XX);\n', text)
    assert_in('\ntransform_scale(YY);\n', text)

    # test pre/post assignments
    fun = Function('void main() {some stuff;}')
    fun['pre'] = '__pre__'
    fun['post'] = '__post__'
    text = fun.compile()
    assert text == 'void main() {\n    __pre__\nsome stuff;\n    __post__\n}\n'

    # Test variable expressions
    fun = Function('void main(){$foo; $bar;}')
    fun['foo'] = Variable('uniform float bla')
    fun['bar'] = Variable('attribute float bla')
    assert_is(type(fun['foo']), Variable)
    assert_is(type(fun['bar']), Variable)
    assert_in(fun['foo'], fun.dependencies())
    assert_in(fun['bar'], fun.dependencies())

    # Test special variables
    fun = Function('void main(){$foo; $bar;}')
    variable = Variable('attribute vec3 v_pos')
    varying = Variable('varying vec3 color')
    # These do not work due to index
    assert_raises(TypeError, fun.__setitem__, 3, 3)  # not a string
    assert_raises(KeyError, fun.__setitem__, 'xxx', 3)  # unknown template var
    assert_raises(TypeError, fun.__setitem__, variable, 3)  # only varyings
    # These work
    fun['gl_PointSize'] = '3.0'
    fun[varying] = variable
    # And getting works
    assert_equal(fun['gl_PointSize'].text, '3.0')
    assert_equal(fun[varying], variable)


def test_function_changed():
    ch = []

    class C(object):
        def _dep_changed(self, dep, **kwargs):
            ch.append(dep)
    ch_obj = C()

    def assert_changed(*objs):
        assert set(ch) == set(objs)
        while ch:
            ch.pop()

    fun1 = Function('void main(){$var1; $var2;}')
    fun1._dependents[ch_obj] = None
    fun1['var1'] = 'x'
    fun1['var2'] = 'y'
    assert_changed(fun1)

    fun1['var1'] = 'z'
    assert_changed(fun1)

    # same value; should result in no change events
    fun1['var1'] = 'z'
    assert_changed()

    fun1['var1'] = 0.5
    var1 = fun1['var1']
    var1._dependents[ch_obj] = None
    assert_changed(fun1)

    var1.name = 'xxx'
    assert_changed(fun1, var1)

    # changing type requires code change
    var1.value = 7
    assert_changed(fun1, var1)

    # changing value (but not type) requires no code changes
    var1.value = 6
    assert_changed()

    # test variable disconnect
    fun1['var1'] = Variable('var1', 7)
    var2 = fun1['var1']
    var2._dependents[ch_obj] = None
    # assert_changed(fun1)
    # var2 is now connected
    var2.value = (1, 2, 3, 4)
    assert_changed(fun1, var2)
    # ..but var1 no longer triggers fun1.changed
    assert_changed()
    var1.value = 0.5
    assert_changed(var1)

    # test expressions
    fun2 = Function('float fn(float x){return $var1 + x;}')
    fun3 = Function('float fn(float x){return $var1 + x;}')
    exp1 = fun2(fun3(0.5))
    fun1['var2'] = exp1
    assert_changed(fun1)

    fun2._dependents[ch_obj] = None
    fun3._dependents[ch_obj] = None
    exp1._dependents[ch_obj] = None

    fun2['var1'] = 'x'
    assert_changed(fun1, fun2, exp1)

    fun3['var1'] = 'x'
    assert_changed(fun1, fun3, exp1)

    # test disconnect
    fun1['var2'] = fun2
    assert_changed(fun1)
    # triggers change
    fun2['var1'] = 0.9
    assert_changed(fun1, fun2, exp1)
    # no longer triggers change
    fun3['var1'] = 0.9
    assert_changed(fun3, exp1)


def test_FunctionChain():

    f1 = Function("void f1(){}")
    f2 = Function("void f2(){}")
    f3 = Function("float f3(vec3 x){}")
    f4 = Function("vec3 f4(vec3 y){}")
    f5 = Function("vec3 f5(vec4 z){}")

    ch = FunctionChain('chain', [f1, f2])
    assert ch.name == 'chain'
    assert ch.args == []
    assert ch.rtype == 'void'

    assert_in('f1', ch.compile())
    assert_in('f2', ch.compile())

    ch.remove(f2)
    assert_not_in('f2', ch.compile())

    ch.append(f2)
    assert_in('f2', ch.compile())

    ch = FunctionChain(funcs=[f5, f4, f3])
    assert_equal('float', ch.rtype)
    assert_equal([('vec4', 'z')], ch.args)
    assert_in('f3', ch.compile())
    assert_in('f4', ch.compile())
    assert_in('f5', ch.compile())
    assert_in(f3, ch.dependencies())
    assert_in(f4, ch.dependencies())
    assert_in(f5, ch.dependencies())


def test_StatementList():
    func = Function("void func() {}")
    main = Function("void main() {}")
    main['pre'] = StatementList()
    expr = func()
    main['pre'].add(expr, 0)
    assert list(main['pre'].items) == [expr]
    main['pre'].add(expr)
    assert list(main['pre'].items) == [expr]

    code = main.compile()
    assert " func();" in code

    main['pre'].remove(expr)
    assert list(main['pre'].items) == []


def test_MainFunction():
    code = """
    const float pi = 3.0;  // close enough.
    
    vec4 rotate(vec4 pos) {
        return pos;  // just kidding.
    }
    
    attribute mat4 m_transform;
    attribute vec4 a_pos;
    void main() {
        gl_Position = m_transform * a_pos;
    }
    """

    mf = MainFunction('vertex', code)

    assert mf.name == 'main'
    assert mf.rtype == 'void'
    assert len(mf.args) == 0
    sn = set(mf.static_names())
    assert sn == set(['pi', 'rotate', 'pos', 'm_transform', 'a_pos'])


if __name__ == '__main__':
    for key in [key for key in globals()]:
        if key.startswith('test_'):
            func = globals()[key]
            print('running', func.__name__)
            func()

    # Uncomment to run example
    print('='*80)
    test_example1()


run_tests_if_main()
