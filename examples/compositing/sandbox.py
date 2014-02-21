"""
Sandbox for experimenting with vispy.shaders.composite

"""

presets = [
('TEST', '''
 
from vispy.shaders.composite import CompositeProgram, Function


vertex_shader = """
vec4 input_position();

void main() {
    gl_Position = input_position();
}
"""

fragment_shader = """
void main() {
}
"""

program = CompositeProgram(vertex_shader, fragment_shader)

# Function templates allow the creation of new functions by using string.Template 
# to fill in names of the function and the program variables it depends on.
flatten = Function("""
    vec4 $func_name() {
        vec4 pos = $vec4_pos;
        pos.z = 0;
        pos.w = 1;
        return pos;
    }
    """)

# Note the bindings argument above; this is required because there is otherwise
# no way to determine the type of the variable 'pos'.

# As with the previous Function example, we use bind() to create a new Function 
# with the correct name and program variables.
bound = flatten.wrap('input_position', pos=('attribute', 'position_u'))

program.set_hook('input_position', bound)


# obligatory: these variables are used to fill the text fields on the right.
VERTEX, FRAGMENT = program._generate_code()
 
 
 
'''
),

('Introduction', '''
"""
             ------ Shader Composition Sandbox -------

Instructions:

1) Edit this code; it is immediately executed after every change. Exceptions
   will be displayed on the right side.
   
2) Assign strings to VERTEX and FRAGMENT variables (see below) and they will
   appear in the windows to the right. 

3) Select presets from the list above to see a few examples.

"""


from vispy.shaders.composite import CompositeProgram

vertex_shader = "void main() {}"
fragment_shader = "void main() {}"

program = CompositeProgram(vertex_shader, fragment_shader)

# obligatory: these variables are used to fill the text fields on the right.
VERTEX, FRAGMENT = program._generate_code()
'''),


('Simple hook', '''
"""
In this example we define a 'hook' in the vertex shader: a function prototype
with no definition. By leaving this function undefined, any new function 
definition may be concatenated to the shader.
"""

from vispy.shaders.composite import CompositeProgram, Function

# The hook is called 'input_position', and is used to provide the
# value for gl_Position. 
vertex_shader = """
vec4 input_position();

void main() {
    gl_Position = input_position();
}
"""

fragment_shader = """
void main() {
}
"""

# CompositeProgram parses the shader code for function prototypes
# and registers each as a hook.
program = CompositeProgram(vertex_shader, fragment_shader)

# Now we make a new function definition and attach it to the program.
func = Function("""
    vec4 input_position() {
        return vec4(0,0,0,0);
    }
    """)

program.set_hook('input_position', func)


# obligatory: these variables are used to fill the text fields on the right.
VERTEX, FRAGMENT = program._generate_code()
'''),


('Function wrappers', '''
"""
Here we assign a function to a hook with the wrong name; a wrapper
function is automatically generated with the correct name.
"""

from vispy.shaders.composite import CompositeProgram, Function


vertex_shader = """
vec4 input_position();

void main() {
    gl_Position = input_position();
}
"""

fragment_shader = """
void main() {
}
"""

program = CompositeProgram(vertex_shader, fragment_shader)

# The name of this function does not match the name of the hook.
func = Function("""
    vec4 my_function() {
        return vec4(0,0,0,0);
    }
    """)

# .. but the CompositeProgram will automatically create a wrapper function
# with the correct name.
program.set_hook('input_position', func)


# obligatory: these variables are used to fill the text fields on the right.
VERTEX, FRAGMENT = program._generate_code()
'''),


('Function wrapping (manual)', '''
"""
This example introduces the rationale for function wrapping, 
which allows a function's arguments to be bound to program variables. 

This example does the task manually; the next example will do it 
automatically.
"""

from vispy.shaders.composite import CompositeProgram, Function


vertex_shader = """
vec4 input_position();

void main() {
    gl_Position = input_position();
}
"""

fragment_shader = """
void main() {
}
"""

program = CompositeProgram(vertex_shader, fragment_shader)

# This function has the wrong signature to be attached to input_position.
func = Function("""
    vec4 flatten_pos(vec4 pos) {
        pos.z = 0;
        pos.w = 1;
        return pos;
    }
    """)

# Because this function cannot be ised as a definition for input_position, 
# we will need another function that wraps it, providing input to the pos argument.
# First we'll do it manually, and in the next example it will be automatic:
wrapper = Function("""
    attribute vec4 position_u;
    vec4 input_position() {
        return flatten(position_u);
    }
    """,
    deps=[func])

# Note the 'deps' argument above, which ensures that *func* will be included
# wherever *wrapper* is.
    
program.set_hook('input_position', wrapper)


# obligatory: these variables are used to fill the text fields on the right.
VERTEX, FRAGMENT = program._generate_code()

'''),


('Function binding (automatic)', '''
"""
This example shows how to automatically bind a function's arguments
to program variables using Function.bind().

Binding facilitates the separation of function code from the names of program
variables. This is essential for compositing because modular components
cannot be guaranteed access to any particular program variable.
"""

from vispy.shaders.composite import CompositeProgram, Function


vertex_shader = """
vec4 input_position();

void main() {
    gl_Position = input_position();
}
"""

fragment_shader = """
void main() {
}
"""

program = CompositeProgram(vertex_shader, fragment_shader)

# This function has the wrong signature to be attached to input_position.
func = Function("""
    vec4 flatten_pos(vec4 pos) {
        pos.z = 0;
        pos.w = 1;
        return pos;
    }
    """)

# Because this function cannot be ised as a definition for input_position, 
# we will need another function that wraps it, providing input to the pos argument.
wrapper = func.wrap('input_position', pos=('attribute', 'position_u'))

program.set_hook('input_position', wrapper)


# obligatory: these variables are used to fill the text fields on the right.
VERTEX, FRAGMENT = program._generate_code()
'''),


('Function templates', '''
"""
Function binding is very useful, but it makes a mess of the shader code by 
doubling the number of function definitions. An alternative (but nearly 
equivalent) approach is to use FunctionTemplate.

In most cases, it is preferred to use FunctionTemplate instead of Function.
Occasionally, we may have a large function that must be bound multiple
times; in this case it may be preferrable to use Function instead.
"""

from vispy.shaders.composite import CompositeProgram, Function


vertex_shader = """
vec4 input_position();

void main() {
    gl_Position = input_position();
}
"""

fragment_shader = """
void main() {
}
"""

program = CompositeProgram(vertex_shader, fragment_shader)

# Function templates allow the creation of new functions by using string.Template 
# to fill in names of the function and the program variables it depends on.
flatten = Function("""
    vec4 $func_name() {
        vec4 pos = $vec4_pos;
        pos.z = 0;
        pos.w = 1;
        return pos;
    }
    """)

# Note the bindings argument above; this is required because there is otherwise
# no way to determine the type of the variable 'pos'.

# As with the previous Function example, we use bind() to create a new Function 
# with the correct name and program variables.
bound = flatten.wrap('input_position', pos=('attribute', 'position_u'))

program.set_hook('input_position', bound)


# obligatory: these variables are used to fill the text fields on the right.
VERTEX, FRAGMENT = program._generate_code()
'''),

('Function chaining', '''
"""
Function chains are another essential component of shader composition,
allowing a list of functions to be executed in order.
"""

from vispy.shaders.composite import (CompositeProgram, Function, FunctionChain)

# Added a new hook to allow any number of functions to be executed
# after gl_Position is set.
vertex_shader = """
vec4 input_position();
void vert_post_hook();

void main() {
    gl_Position = input_position();
    vert_post_hook();
}
"""

fragment_shader = """
void main() {
}
"""

program = CompositeProgram(vertex_shader, fragment_shader)

pos_func = Function("""
    vec4 input_position() {
        return vec4(0,0,0,0);
    } """)
program.set_hook('input_position', pos_func)

# Add a function to flatten the z-position of the vertex
flatten = Function("""
    void flatten_func() {
        gl_Position.z = 0;
    }
    """)

# Add another function that copies an attribute to a varying
# for use in the fragment shader
read_attr = Function("""
    void $func_name() {
        $vec4_output = $vec4_input;
    }
    """)

# ..and bind this to two new program variables
read_attr_bound = read_attr.wrap(name='read_attr_func', 
                                 input=('attribute', 'data_a'),
                                 output=('varying', 'data_v'))

# Now create a chain that calls both functions in sequence
post_chain = FunctionChain('vert_post_hook', [flatten, read_attr_bound])

program.set_hook('vert_post_hook', post_chain)


# obligatory: these variables are used to fill the text fields on the right.
VERTEX, FRAGMENT = program._generate_code()
'''),


('Transform chaining', '''
"""
Function chains may also be generated from a list of functions that require a 
single input argument. The return value of each function call supplies the
input to the next argument, such that the original input is transformed in a
series steps. 

This is most commonly used for passing vertex positions through a series
of transform functions.
"""

from vispy.shaders.composite import (CompositeProgram, Function, FunctionChain)


vertex_shader = """
vec4 input_position();

void main() {
    gl_Position = input_position();
}
"""

fragment_shader = """
void main() {
}
"""

program = CompositeProgram(vertex_shader, fragment_shader)

flatten = Function("""
    vec4 flatten_func(vec4 pos) {
        pos.z = 0;
        pos.w = 1;
        return pos;
    }
    """)

# Define a scaling function
scale = Function("""
    vec4 $func_name(vec4 pos) {
        return pos * vec4($vec3_scale, 1);
    }
    """)

# ..and bind it to use 'uniform vec3 scale_u' as its scale factor
scale_bound = scale.wrap('scale_func', scale=('uniform', 'scale_u'))

# Now create a chain that calls flatten and scale_bound in order, passing
# the return value of each call to the input of the next:
transform = FunctionChain('transform', [flatten, scale_bound])

# finally, bind the input of the new chain function to an attribute.
bound = transform.wrap('input_position', pos=('attribute', 'position_u'))

program.set_hook('input_position', bound)


# obligatory: these variables are used to fill the text fields on the right.
VERTEX, FRAGMENT = program._generate_code()

'''),




('Fragment shaders (manual)', '''
"""
Although the prior examples focused on vertex shaders, these concepts 
apply equally well for fragment shaders.

However: fragment shaders have one limitation that makes them very
different--they lack attributes. In order to supply attribute data
to a fragment shader, we will need to introduce some supporting code
to the vertex shader.

This example is a manual demonstration; the next will automate the 
same procedure.
"""

from vispy.shaders.composite import (CompositeProgram, Function, FunctionChain)

# we require a void hook in the vertex shader that can be used 
# to attach supporting code for the fragment shader.
vertex_shader = """
void vert_post_hook();

void main() {
    gl_Position = vec4(0,0,0,0);
    vert_post_hook();
}
"""

# add a hook to the fragment shader to allow arbitrary color input
fragment_shader = """
vec4 fragment_color();

void main() {
    gl_FragColor = fragment_color();
}
"""

program = CompositeProgram(vertex_shader, fragment_shader)

# First, define a simple fragment color function and bind it to a varying
# input:
frag_func = Function("vec4 $func_name() { return $vec4_input; }")
frag_func_bound = frag_func.wrap(name='fragment_color',
                                 input=('varying', 'color_var'))

# Attach to the program
program.set_hook('fragment_color', frag_func_bound)

# Next, we need a vertex shader function that will supply input 
# to the varying.
vert_func = Function("void $func_name() { $vec4_output = $vec4_input; }")

# Now we bind the vertex support to both the varying and a new input attribute.
vert_func_bound = vert_func.wrap(name='frag_color_support',
                                 input=('attribute', 'color_a'),
                                 output=('varying', 'color_var'))

# Note #1: The output varing is given the same name 'color_var' as the input 
#          varying to the fragment function. This is crucial!
# Note #2: We *could* have bound the vert_func to name='vert_post_hook' and
#          attached it directly to the vertex shader, but instead we will 
#          install a function chain and attach vert_func to that.

# Automatically attach a new FunctionChain to *vert_post_hook*:
program.add_chain('vert_post_hook')

# ..and attach the support function to the chain:
program.add_callback('vert_post_hook', vert_func_bound)


# obligatory: these variables are used to fill the text fields on the right.
VERTEX, FRAGMENT = program._generate_code() 
'''),




('Fragment shaders (automatic)', '''
"""
This example automates the work done in the previous example "Fragment
shaders (manual)".
"""

from vispy.shaders.composite import (CompositeProgram, Function, FragmentFunction)

# we require a void hook in the vertex shader that can be used 
# to attach supporting code for the fragment shader.
vertex_shader = """
void vert_post_hook();

void main() {
    gl_Position = vec4(0,0,0,0);
    vert_post_hook();
}
"""

# add a hook to the fragment shader to allow arbitrary color input
fragment_shader = """
vec4 fragment_color();

void main() {
    gl_FragColor = fragment_color();
}
"""

program = CompositeProgram(vertex_shader, fragment_shader)

# Start by defining both the fragment function we'd like to install
# and the required vertex shader support code:
frag_func = Function("vec4 $func_name() { return $vec4_input; }")
vert_func = Function("void $func_name() { $vec4_output = $vec4_input; }")

# Now combine these into a single object:
combined = FragmentFunction(frag_func, vert_func,
                            link_vars=[('output', 'input')],
                            vert_hook='vert_post_hook')
# The 'link_vars' argument specifies that the vertex shader 'output' and
# the fragment shader 'input' must be bound to the same varying.

# The 'vert_hook' argument specifies a chain in the vertex shader to which 
# the support code will be attached.

frag_bound = combined.wrap('fragment_color',
                           input=('attribute', 'color_a'))

# As in the previous example, attach a new FunctionChain to *vert_post_hook*:
program.add_chain('vert_post_hook')

# and finally attach the fragment code
# (at this point, the supporting vertex code will be automaticaly attached as well)
program.set_hook('fragment_color', frag_bound)


# obligatory: these variables are used to fill the text fields on the right.
VERTEX, FRAGMENT = program._generate_code() 
'''),

]








from PyQt4 import QtCore
from PyQt4.QtGui import *
import sys, traceback

from editor import Editor, HAVE_QSCI

qsci_note = """
#  [[ NOTE: Install PyQt.QsciScintilla for improved code editing ]]
#  [[ (Debian packages: python-qscintilla2 or python3-pyqt4.qsci ]]

"""
if not HAVE_QSCI:
    presets[0] = (presets[0][0], qsci_note + presets[0][1])


app = QApplication([])

win = QMainWindow()
cw = QWidget()
win.setCentralWidget(cw)
layout = QGridLayout()
cw.setLayout(layout)

editor = Editor(language='Python')
vertex = Editor(language='CPP')
fragment = Editor(language='CPP')

hsplit = QSplitter(QtCore.Qt.Horizontal)
vsplit = QSplitter(QtCore.Qt.Vertical)

layout.addWidget(hsplit)
hsplit.addWidget(editor)
hsplit.addWidget(vsplit)
vsplit.addWidget(vertex)
vsplit.addWidget(fragment)

menubar = win.menuBar()

last_loaded = -1
def load_example(name):
    global last_loaded
    if isinstance(name, int):
        code = presets[name][1]
        editor.setText(code)
        last_loaded = name
    else:
        for i, preset in enumerate(presets):
            n, code = preset
            if n == name:
                editor.setText(code)
                last_loaded = i
                return

def load_next():
    global last_loaded
    try:
        load_example(last_loaded+1)
    except IndexError:
        pass

def mk_load_callback(name):
    return lambda: load_example(name)
    
import functools
example_menu = menubar.addMenu('Load example..')
for i, preset in enumerate(presets):
    name = preset[0]
    action = example_menu.addAction("%d. %s" % (i,name), mk_load_callback(name))
    
next_action = menubar.addAction("Next example", load_next)

win.show()
win.resize(1000,800)
hsplit.setSizes([700, 300])

load_example(0)

def update():
    code = editor.text()
    local = {}
    glob = {}
    try:
        exec(code, local, glob)
        vert = glob['VERTEX']
        frag = glob['FRAGMENT']
        editor.clear_marker()
    except:
        vert = traceback.format_exc()
        frag = ""
        tb = sys.exc_info()[2]
        while tb is not None:
            #print(tb.tb_lineno, tb.tb_frame.f_code.co_filename)
            if tb.tb_frame.f_code.co_filename == '<string>':
                editor.set_marker(tb.tb_lineno-1)
            tb = tb.tb_next
        
    vertex.setText(vert)
    fragment.setText(frag)
    
editor.textChanged.connect(update)
update()    
    
app.exec_()
