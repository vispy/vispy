"""
Sandbox for experimenting with vispy.shaders.composite

"""

presets = [
    
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


('Function binding (manual)', '''

"""
This example introduces the rationale for function binding, 
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
wrapper = func.bind('input_position', pos=('attribute', 'position_u'))

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

from vispy.shaders.composite import CompositeProgram, FunctionTemplate


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
flatten = FunctionTemplate("""
    vec4 $func_name() {
        vec4 pos = $pos;
        pos.z = 0;
        pos.w = 1;
        return pos;
    }
    """,
    bindings=[('vec4 pos')])

# Note the bindings argument above; this is required because there is otherwise
# no way to determine the type of the variable 'pos'.

# As with the previous Function example, we use bind() to create a new Function 
# with the correct name and program variables.
bound = flatten.bind('input_position', pos=('attribute', 'position_u'))

program.set_hook('input_position', bound)


# obligatory: these variables are used to fill the text fields on the right.
VERTEX, FRAGMENT = program._generate_code()
'''),

('Function chaining', '''


"""
Function chains are another essential component of shader composition,
allowing a list of functions to be executed in order.
"""

from vispy.shaders.composite import (CompositeProgram, Function,
                                     FunctionTemplate, FunctionChain)

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
read_attr = FunctionTemplate("""
    void $func_name() {
        $output = $input;
    }
    """, bindings=[('vec4 output'), ('vec4 input')])

# ..and bind this to two new program variables
read_attr_bound = read_attr.bind(name='read_attr_func', 
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

from vispy.shaders.composite import (CompositeProgram, Function,
                                     FunctionTemplate, FunctionChain)


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
scale = FunctionTemplate("""
    vec4 $func_name(vec4 pos) {
        return pos * vec4($scale, 1);
    }
    """, bindings=[('vec3 scale')])

# ..and bind it to use 'uniform vec3 scale_u' as its scale factor
scale_bound = scale.bind('scale_func', scale=('uniform', 'scale_u'))

# Now create a chain that calls flatten and scale_bound in order, passing
# the return value of each call to the input of the next:
transform = FunctionChain('transform', [flatten, scale_bound])

# finally, bind the input of the new chain function to an attribute.
bound = transform.bind('input_position', pos=('attribute', 'position_u'))

program.set_hook('input_position', bound)


# obligatory: these variables are used to fill the text fields on the right.
VERTEX, FRAGMENT = program._generate_code()

'''),

]








from PyQt4 import QtCore
from PyQt4.QtGui import *
import sys, traceback

from editor import Editor

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
    for i, preset in enumerate(presets):
        n, code = preset
        if n == name:
            editor.setText(code)
            last_loaded = i
            return

def load_next():
    global last_loaded
    try:
        load_example(presets[last_loaded+1][0])
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

load_example('Introduction')

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
