from vispy.scene.shaders.function2 import Function


TransformScale = Function("""
uniform float u_scale;
vec4 transform_scale(vec4 pos)
{
    pos.xyz *= u_scale;
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



# Get function objects. Generate random name for transforms
code = Frag_template.new()
t1 = TransformScale.new()
t2 = TransformZOffset.new()
t3 = TransformScale.new()
t4 = TransformScale.new()

# Compose everything together
code['position'] = t1(t2(t3('attribute vec4 u_position')))
code['correction'] = t1('attribute vec4 u_position')  # Look, we use t1 again, different sig
code['endtransform'] = t4()  # Sig defined in template overrides given sig
code['nlights'] = '4'

t2['offset'] = '1.0'  # We can assign replacements after combining them

# Show result
print(code)

# Yay, we can easil obtain the uniform names via their original function object
#print(t1.uniform('u_scale'), t3.uniform('u_scale'))


##

# Frag_template = Function("""
# void main (void)
# {
#     gl_Position = $position;
# }
# """)
# 
# TransformScale = Function("""
# uniform float u_scale;
# vec4 transform_scale(vec4 pos)
# {
#     pos.xyz *= u_scale;
#     return pos;
# }
# """)
# 
# Position = Function("""
# attribute vec4 a_position;
# vec4 position() {  return a_position; }
# """)
# 
# class Transform(object):
#     def __init__(self):
#         # Equivalent methods to create new function object
#         self.func = Function(TransformScale, name='trans'+hex(id(self)))
#         #self.func = TransformScale.new(name='trans'+hex(id(self))
#     
#     def set_scale(self):
#         name = 'u_scale'
#         real_name = self.func.uniform(name)
#         # .... set uniform using that name
# 
# 
# transforms = [Transform(), Transform(), Transform(), Transform()]
# 
# code = Frag_template.new()
# ob = Position.new()
# for trans in transforms:
#     ob = trans.func(ob)
# code['$position']  = ob
# print(code)
