from nose.tools import assert_raises
from vispy.shaders.composite import *


func = ShaderFunction(code="""
vec3 my_function(vec2 x, float z) {
    return vec3(vec2, z);
}
""")

assert(func.name == 'my_function')
assert(func.rtype == 'vec3')
assert(func.args == [('vec2', 'x'), ('float', 'z')])
    
    
func2 = ShaderFunction(code="""
vec3 my_function2(vec2 x, float z) {
    return vec3(vec2, z);
}
""")

assert(func2.name == 'my_function2')
assert(func2.rtype == 'vec3')
assert(func2.args == [('vec2', 'x'), ('float', 'z')])

    
vmain = """
vec3 my_hook1(vec2 x, float y);
vec3 my_hook2(vec2 x);
vec4 my_hook3(vec4 x);

void main() {
    
}

"""

fmain = """
void main() {
    
}
"""

prog = CompositeProgram(vmain, fmain)

assert_raises(NameError, lambda: prog.set_hook('my_hookX', func))
assert_raises(TypeError, lambda: prog.set_hook('my_hook2', func))

prog.set_hook('my_hook1', func)
bound = func2.bind('my_hook2', z=('uniform', 'float', 'u_input_z'))

assert(bound.name == 'my_hook2')
assert(bound.args == [('vec2', 'x')])
assert(bound.rtype == 'vec3')

prog.set_hook('my_hook2', bound)



fn1 = ShaderFunction("""
vec4 fn1(vec4 x) {
    return x;
}
""")

fn2 = ShaderFunction("""
vec4 fn2(vec4 x) {
    return x;
}
""")

fn3 = ShaderFunction("""
vec4 fn3(vec4 x) {
    return x;
}
""")


chain = ShaderFunctionChain('my_hook3', [fn1, fn2, fn3])
prog.set_hook('my_hook3', chain)

print "\n".join(prog.generate_code())



