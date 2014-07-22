from vispy.scene.shaders.function2 import Function, Variable

# Users normally don't need these, but I want to test them
from vispy.scene.shaders.function2 import FunctionCall, TextExpression

from nose.tools import assert_raises, assert_equal, assert_not_equal
from vispy.testing import assert_in, assert_not_in, assert_is  # noqa


## Define some snippets

TransformScale = Function("""
vec4 transform_scale(vec4 pos)
{
    pos.xyz *= $scale;
    return pos;
}
""")

TransformZOffset = Function("""
vec4 transform_zoffset(vec4 pos)
{
    pos.z += $offset;
    return pos;
}
""")

Frag_template = Function("""
void main(void)
{
    int nlights = $nlights;
    vec4 pos = $position;
    pos += $correction;
    gl_Position = $endtransform(pos);
}

""")


data = 'just some dummy variable, Function is agnostic about this'


## Examples

def test_example1():
    """ Just a few simple compositions.
    """
    
    # Get function objects. Generate random name for transforms
    code = Frag_template.new()
    t1 = TransformScale.new()
    t2 = TransformZOffset.new()
    t3 = TransformScale.new()
    
    # We need to create a variable in order to use it in two places
    pos = Variable('attribute vec4 u_position')
    
    # Compose everything together
    code['position'] = t1(t2(pos))
    code['correction'] = t1(pos)  # Look, we use t1 again, different sig
    code['endtransform'] = t3()  # Sig defined in template overrides given sig
    code['nlights'] = '4'
    t1['scale'] = t2()
    t3['scale'] = 'uniform vec3 u_scale', (3.0, 4.0, 5.0)
    t2['offset'] = '1.0'
    
    # Show result
    print(code)
    
    # Print all variables. Values can associated to variable objects and then
    # set to the shader program later in a loop similar to this:
    print('===== Variables:')
    for var in code.get_variables():
        print(var.name, var.value)


def test_example2():
    """ Demonstrate how a transform would work.
    """
    
    Frag_template = Function("""
    void main(void)
    {
        gl_Position = $position;
    }
    """)
    
    TransformScale = Function("""
    vec4 transform_scale(vec4 pos)
    {
        pos.xyz *= $scale;
        return pos;
    }
    """)
    
    class Transform(object):
        def __init__(self):
            # Equivalent methods to create new function object
            self.func = Function(TransformScale)
            self.func['scale'] = 'uniform float'
            #self.func = TransformScale.new()
        
        def set_scale(self, scale):
            self.func['scale'].value = scale
    
    transforms = [Transform(), Transform(), Transform()]
    
    code = Frag_template.new()
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
    fun = TransformScale.new()
    fun2 = TransformZOffset.new()
    
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
    
    # Test setting text expressions
    assert_raises(ValueError, fun.__setitem__, 'bla', '33')  # no such template
    fun['foo'] = '33'
    fun['bar'] = 'bla bla'
    assert_is(type(fun['foo']), TextExpression)
    assert_equal(fun['foo']._injection(), '33')
    assert_is(type(fun['bar']), TextExpression)
    assert_equal(fun['bar']._injection(), 'bla bla')
    
    # Test setting call expressions
    trans = TransformScale.new()
    fun['foo'] = trans()
    fun['bar'] = trans('3')
    assert_is(type(fun['foo']), FunctionCall)
    assert_equal(fun['foo'].function, trans)
    assert_in(trans, fun._dependencies())
    
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
    
    # todo: Test function calls
    # todo: Test verbatim replacements
    # todo: test actual code output

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
    str(fun1); str(fun2)
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
    
    fun1 = Function('void main(){$var1; $var2;}')
    fun2 = Function('void main(){$var1; $var2;}')
    fun3 = Function('void foo(){$var1; $var2;}')
    # Start uninitialized
    assert_equal(fun1.ischanged(), True)
    # Get code and check
    str(fun1)
    assert_equal(fun1.ischanged(), False)
    # Set function and check again
    fun1['var1'] = fun3()
    assert_equal(fun1.ischanged(), True)
    str(fun3)
    assert_equal(fun1.ischanged(), True)
    str(fun1)
    assert_equal(fun1.ischanged(), False)
    # Set variable on funtcion and try again
    fun3['var1'] = 'uniform float bla'
    assert_equal(fun1.ischanged(), True)
    assert_equal(fun3.ischanged(), True)
    str(fun3)
    assert_equal(fun1.ischanged(), True)
    assert_equal(fun3.ischanged(), False)
    str(fun1)
    assert_equal(fun1.ischanged(), False)
    
    # Dirty when linking
    str(fun1); str(fun2)
    assert_equal(fun1.ischanged(), False)
    assert_equal(fun2.ischanged(), False)
    #
    fun1.link(fun2)
    assert_equal(fun1.ischanged(), True)
    assert_equal(fun2.ischanged(), True)
    #
    str(fun1)
    assert_equal(fun1.ischanged(), False)
    assert_equal(fun2.ischanged(), True)
    str(fun2)
    assert_equal(fun1.ischanged(), False)
    assert_equal(fun2.ischanged(), False)
    
    # Again, but different order
    fun1.link(fun2)
    assert_equal(fun1.ischanged(), True)
    assert_equal(fun2.ischanged(), True)
    #
    str(fun2)
    assert_equal(fun1.ischanged(), True)
    assert_equal(fun2.ischanged(), False)
    str(fun1)
    assert_equal(fun1.ischanged(), False)
    assert_equal(fun2.ischanged(), False)

    

if __name__ == '__main__':
    for key in [key for key in globals()]:
        if key.startswith('test_'):
            func = globals()[key]
            print('running', func.__name__)
            func()
    
    # Uncomment to run example
    print('='*80)
    test_example1()
