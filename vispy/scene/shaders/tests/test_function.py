from vispy.scene.shaders.function2 import Function, Variable

# Users normally don't need these, but I want to test them
from vispy.scene.shaders.function2 import FunctionCall, TextExpression

from nose.tools import assert_raises, assert_equal, assert_not_equal
from vispy.testing import assert_in, assert_not_in, assert_is  # noqa


## Define some snippets

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
    $post_hook
}

""")

frag_template = Function("""
void main(void)
{
    gl_Fragcolor = $color;
}

""")

data = 'just some dummy variable, Function is agnostic about this'


## Examples

def test_example1():
    """ Just a few simple compositions.
    """
    
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
    t1['scale'] = t2()
    t3['scale'] = (3.0, 4.0, 5.0)
    t2['offset'] = '1.0'
    
    code2 = Function(frag_template)
    code.link(code2)
    code2['color'] = Varying('v_position')
    
    code['gl_PointSize'] = '3.0'
    code[code2['color']] = pos
    
    # Show result
    print(code)
    print('=====')
    print(code2)
    
    # Print all variables. Values can associated to variable objects and then
    # set to the shader program later in a loop similar to this:
    print('===== Variables:')
    for var in code2.get_variables():
        print(var.name, var.value)


def test_example2():
    """ Demonstrate how a transform would work.
    """
    
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
            #self.func = Function(transformScale)
        
        def set_scale(self, scale):
            self.func['scale'].value = scale
    
    transforms = [Transform(), Transform(), Transform()]
    
    code = Function(vert_template)
    ob = Variable('attribute vec3 a_position')
    for trans in transforms:
        ob = trans.func(ob)
    code['position'] = ob
    print(code)

## Tests


def test_TextExpression():
    exp = TextExpression('foo bar')
    print(exp)
    assert_in('foo bar', str(exp))
    assert_in(exp.__class__.__name__, str(exp))
    assert_equal(exp._injection(), 'foo bar')
    assert_raises(ValueError, TextExpression, 4)


def test_FunctionCall():
    fun = Function(transformScale)
    fun2 = Function(transformZOffset)
    
    # No args
    call = fun()
    # Test repr
    print(call)
    assert_in(fun.name, str(call))
    assert_in(call.__class__.__name__, str(call))
    # Test sig
    assert len(call._signature) == 0
    assert_equal(call._injection(), fun.name+'()')
    # Test dependencies
    assert_in(fun, call._dependencies())
    
    # More args
    call = fun('foo', fun2())
    # Test repr
    print(call)
    assert_in(fun.name, str(call))
    assert_in('foo', str(call))
    assert_in(fun2.name, str(call))
    # Test sig
    assert len(call._signature) == 2
    # Test dependencies
    assert_in(fun, call._dependencies())
    assert_in(fun2, call._dependencies())

    # Wrong arg
    assert_raises(TypeError, FunctionCall, 4)
    assert_raises(ValueError, FunctionCall, 4, 4)


def test_Variable():
    
    # Test init fail
    assert_raises(TypeError, Variable)  # no args
    assert_raises(ValueError, Variable, 3)  # need string
    assert_raises(ValueError, Variable, 'blabla')  # need correct vtype
    assert_raises(ValueError, Variable, 'bla bla')  # need correct vtype
    assert_raises(ValueError, Variable, 'uniform_bla')  # need spaces
    assert_raises(ValueError, Variable, 'uniform b l a')  # too many
    assert_raises(ValueError, Variable, 'uniform bla')  # need name
    
    # Test init success
    var = Variable('uniform float bla')  # Finally
    assert_equal(var.name, 'bla')
    assert var.value is None
    var = Variable('uniform float', altname='bla')  # Also valid
    assert_equal(var.name, 'bla')
    assert var.value is None
    
    # Test value
    var = Variable('uniform float bla', data)  # Also valid
    assert_equal(var.value, data)
    var.value = 3
    assert_equal(var.value, 3)
    
    # Test repr
    var = Variable('uniform float bla')
    print(var)
    assert_in(var.__class__.__name__, str(var))
    assert_in('uniform float bla', str(var))
    
    # Test injection, definition, dependencies
    assert_equal(var._injection(), var.name)
    assert_equal(var._definition(), 'uniform float bla;')
    assert_in(var, var._dependencies())
    
    # Renaming
    var = Variable('uniform float bla')
    assert_equal(var.name, 'bla')
    var._rename('foo')
    assert_equal(var.name, 'foo')
    

def test_function_basics():
    
    # Test init fail
    assert_raises(TypeError, Function)  # no args
    assert_raises(ValueError, Function, 3)  # need string
    assert_raises(ValueError, Function, '')  # no code

    # Test init success 1
    fun = Function('void main(){}')
    assert_equal(fun.name, 'main')
    assert len(fun._template_vars) == 0
    
    # Test init success with template vars
    fun = Function('void main(){$foo; $bar;}')
    assert_equal(fun.name, 'main')
    assert len(fun._template_vars) == 2
    assert_in('foo', fun._template_vars)
    assert_in('bar', fun._template_vars)
    
    # Test setting verbatim expressions
    assert_raises(KeyError, fun.__setitem__, 'bla', '33')  # no such template
    fun['foo'] = '33'
    fun['bar'] = 'bla bla'
    assert_is(type(fun['foo']), TextExpression)
    assert_equal(fun['foo']._injection(), '33')
    assert_is(type(fun['bar']), TextExpression)
    assert_equal(fun['bar']._injection(), 'bla bla')
    
    # Test setting call expressions
    fun = Function('void main(){\n$foo;\n$bar;\n$spam(XX);\n$eggs(YY);\n}')
    trans = Function(transformScale)
    fun['foo'] = trans()
    fun['bar'] = trans('3', '4')
    fun['spam'] = trans()
    fun['eggs'] = trans('3', '4')
    #
    for name in ['foo', 'bar', 'spam', 'eggs']:
        assert_is(type(fun[name]), FunctionCall)
        assert_equal(fun[name].function, trans)
        assert_in(trans, fun._dependencies())
    #
    text = str(fun)
    assert_in('\ntransform_scale();\n', text)
    assert_in('\ntransform_scale(3, 4);\n', text)
    assert_in('\ntransform_scale(XX);\n', text)
    assert_in('\ntransform_scale(YY);\n', text)
    
    # Test variable expressions
    fun = Function('void main(){$foo; $bar;}')
    fun['foo'] = 'uniform float bla'
    fun['bar'] = 'attribute float bla'
    assert_is(type(fun['foo']), Variable)
    assert_is(type(fun['bar']), Variable)
    assert_in(fun['foo'], fun._dependencies())
    assert_in(fun['bar'], fun._dependencies())
    # Test basic name mangling
    assert_equal(fun['foo'].name, fun['bar'].name)  # Still the sae
    str(fun)  # force name mangling
    assert_not_equal(fun['foo'].name, fun['bar'].name) 
    
    # Test special variables
    fun = Function('void main(){$foo; $bar;}')
    variable = Variable('attribute vec3 v_pos')
    varying = Variable('varying vec3 color')
    # These do not work due to index
    assert_raises(KeyError, fun.__setitem__, 3, 3)  # not a string
    assert_raises(KeyError, fun.__setitem__, 'xxx', 3)  # unknown template var
    assert_raises(KeyError, fun.__setitem__, variable, 3)  # only varyings
    # These do not work due to value
    assert_raises(ValueError, fun.__setitem__, 'gl_PointSize', 3)
    assert_raises(ValueError, fun.__setitem__, varying, 3)
    # These work
    fun['gl_PointSize'] = '3.0'
    fun[varying] = variable
    # And getting works
    assert_equal(fun['gl_PointSize'].text, '3.0')
    assert_equal(fun[varying], variable)
    

def test_function_names():
    
    # Test more complex name mangling
    fun1 = Function('void main(){$var1; $funccall;}')
    fun2 = Function('void a_func(){$var2; $var3;}')
    fun1['var1'] = 'uniform float bla'
    fun1['funccall'] = fun2()  # Set after setting var1 so var1 comes first
    fun2['var2'] = 'uniform float bla'
    fun2['var3'] = 'uniform float bla'
    # Compile fun2, var1 is not mangled yet
    str(fun2)
    assert_equal(fun1['var1'].name, 'bla')
    assert_equal(fun2['var2'].name, 'bla_1')
    assert_equal(fun2['var3'].name, 'bla_2')
    # Compile fun1, all vars are mangled
    str(fun1)
    assert_equal(fun1['var1'].name, 'bla_1')
    assert_equal(fun2['var2'].name, 'bla_2')
    assert_equal(fun2['var3'].name, 'bla_3')
    # Compile fun1, but mangling is unchanged now
    str(fun2)
    assert_equal(fun1['var1'].name, 'bla_1')
    assert_equal(fun2['var2'].name, 'bla_2')
    assert_equal(fun2['var3'].name, 'bla_3')


def test_function_linking():
    
    # Test linking with wrong args
    fun1 = Function('void main(){$var1; $var2;}')
    fun2 = Function('void foo(){$var1; $var2;}')
    assert_raises(ValueError, fun1.link, 3)
    assert_raises(ValueError, fun1.link, fun2)
    assert_raises(ValueError, fun2.link, fun1)
    
    # Test linking shaders
    fun1 = Function('void main(){$var1; $var2;}')
    fun2 = Function('void main(){$var1; $var2;}')
    fun1['var1'] = 'uniform float bla'
    fun1['var2'] = 'uniform float bla'
    fun2['var1'] = 'uniform float bla'
    fun2['var2'] = 'uniform float bla'
    # The two functions are separate
    str(fun1)
    str(fun2)
    assert_equal(fun1['var1'].name, 'bla_1')
    assert_equal(fun1['var2'].name, 'bla_2')
    assert_equal(fun2['var1'].name, 'bla_1')
    assert_equal(fun2['var2'].name, 'bla_2')
    assert_equal(len(fun1.get_variables()), 2)
    assert_equal(len(fun2.get_variables()), 2)
    # Now link!
    fun1.link(fun2)
    str(fun1)
    assert_equal(fun1['var1'].name, 'bla_1')
    assert_equal(fun1['var2'].name, 'bla_2')
    assert_equal(fun2['var1'].name, 'bla_3')
    assert_equal(fun2['var2'].name, 'bla_4')
    assert_equal(len(fun1.get_variables()), 4)
    assert_equal(fun2.get_variables(), fun2.get_variables())


def test_function_changed():
    ch = []
    def on_change(event):
        ch.append(event.source)
        
    def assert_changed(*objs):
        assert set(ch) == set(objs)
        while ch:
            ch.pop()
        
    fun1 = Function('void main(){$var1; $var2;}')
    fun1.changed.connect(on_change)
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
    var1.changed.connect(on_change)
    assert_changed(fun1)
    
    # changing type requires code change
    var1.value = 7
    assert_changed(fun1, var1)

    # changing value (but not type) requires no code changes
    var1.value = 6
    assert_changed()

    # test variable disconnect
    fun1['var1'] = 7
    var2 = fun1['var1']
    var2.changed.connect(on_change)
    assert_changed(fun1)
    # var2 is now connected
    var2.value = (1, 2, 3, 4)
    assert_changed(fun1, var2)
    # ..but var1 no longer triggers fun1.changed
    var1.value = 0.5
    assert_changed(var1)

    # test expressions
    fun2 = Function('float fn(float x){return $var1 + x;}')
    fun3 = Function('float fn(float x){return $var1 + x;}')
    exp1 = fun2(fun3(0.5))
    fun1['var2'] = exp1
    assert_changed(fun1)
    
    fun2.changed.connect(on_change)
    fun3.changed.connect(on_change)
    exp1.changed.connect(on_change)
    
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
    

if __name__ == '__main__':
    for key in [key for key in globals()]:
        if key.startswith('test_'):
            func = globals()[key]
            print('running', func.__name__)
            func()
    
    # Uncomment to run example
    print('='*80)
    test_example1()
