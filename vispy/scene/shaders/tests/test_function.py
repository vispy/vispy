from vispy.scene.shaders.function2 import Function, Variable

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

if __name__ == '__main__':
    test_example1()
    test_example2()
