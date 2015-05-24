# -*- coding: utf-8 -*-
# vispy: testskip
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Sandbox for experimenting with vispy.visuals.shaders
"""
from PyQt4 import QtCore
from PyQt4.QtGui import *  # noqa
import sys
import traceback

from editor import Editor, HAVE_QSCI


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


from vispy.visuals.shaders import ModularProgram

vertex_shader = "void main() {}"
fragment_shader = "void main() {}"

program = ModularProgram(vertex_shader, fragment_shader)

# obligatory: these variables are used to fill the text fields on the right.
program._compile()
VERTEX = program.vert_code
FRAGMENT = program.frag_code
'''),


    ('Simple hook', '''
"""
In this example we define a 'hook' in the vertex shader: a function prototype
with no definition. By leaving this function undefined, any new function
definition may be concatenated to the shader.
"""

from vispy.visuals.shaders import ModularProgram, Function

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

# ModularProgram parses the shader code for function prototypes
# and registers each as a hook.
program = ModularProgram(vertex_shader, fragment_shader)

# Now we make a new function definition and attach it to the program.
func = Function("""
    vec4 input_position() {
        return vec4(0,0,0,0);
    }
    """)

program['input_position'] = func


# obligatory: these variables are used to fill the text fields on the right.
program._compile()
VERTEX = program.vert_code
FRAGMENT = program.frag_code
'''),


    ('Anonymous functions', '''
"""
Functions may optionally be defined with '$' in front of the function name.
This indicates that the function is anonymous (has no name) and thus may be
assigned any new name in the program.

The major benefit to using anonymous functions is that the modular shader
system is free to rename functions that would otherwise conflict with each
other.

In this example, an anonymous function is assigned to a hook. When it is
compiled into the complete program, it is renamed to match the hook.
"""

from vispy.visuals.shaders import ModularProgram, Function

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

program = ModularProgram(vertex_shader, fragment_shader)

# Now we make a new function definition and attach it to the program.
# Note that this function is anonymous (name begins with '$') and does not
# have the correct name to be attached to the input_position hook.
func = Function("""
    vec4 $my_function() {
        return vec4(0,0,0,0);
    }
    """)

program['input_position'] = func


# obligatory: these variables are used to fill the text fields on the right.
program._compile()
VERTEX = program.vert_code
FRAGMENT = program.frag_code
'''),


    ('Program variables', '''
"""
Many Functions need to define their own program variables
(uniform/attribute/varying) in order to operate correctly. However, with many
independent functions added to a ModularProgram, it is likely that two
Functions might try to define variables of the same name.

To solve this, Functions may use $anonymous_variables that will be assigned to
a real program variable at compile time.

In the next example, we will see how ModularProgram resolves name conflicts.
"""

from vispy.visuals.shaders import ModularProgram, Function
import numpy as np

vertex_shader = """
vec4 transform_position(vec4);

attribute vec4 position_a;

void main() {
    gl_Position = transform_position(position_a);
}
"""

fragment_shader = """
void main() {
}
"""

program = ModularProgram(vertex_shader, fragment_shader)

# Define a function to do a matrix transform.
# The variable $matrix will be substituted with a uniquely-named program
# variable when the function is compiled.
func = Function("""
    vec4 $matrix_transform(vec4 pos) {
        return $matrix * pos;
    }
    """)

# The definition for 'matrix' must indicate the variable type and data type.
func['matrix'] = ('uniform', 'mat4', np.eye(4))


program.set_hook('transform_position', func)


# obligatory: these variables are used to fill the text fields on the right.
program._compile()
VERTEX = program.vert_code
FRAGMENT = program.frag_code

'''),


    ('Resolving name conflicts', '''
"""
When anonymous functions and variables have conflicting names, the
ModularProgram will generate unique names by appending _N to the end of the
name.

This example demonstrates dynamic naming of a program variable.
"""

from vispy.visuals.shaders import ModularProgram, Function
import numpy as np

vertex_shader = """
vec4 projection(vec4);
vec4 modelview(vec4);

attribute vec4 position_a;

void main() {
    gl_Position = projection(modelview(position_a));
}
"""

fragment_shader = """
void main() {
}
"""

program = ModularProgram(vertex_shader, fragment_shader)

# Define two identical functions
projection = Function("""
    vec4 $matrix_transform(vec4 pos) {
        return $matrix * pos;
    }
    """)
projection['matrix'] = ('uniform', 'mat4', np.eye(4))

modelview = Function("""
    vec4 $matrix_transform(vec4 pos) {
        return $matrix * pos;
    }
    """)
modelview['matrix'] = ('uniform', 'mat4', np.eye(4))


program.set_hook('projection', projection)
program.set_hook('modelview', modelview)


# obligatory: these variables are used to fill the text fields on the right.
program._compile()
VERTEX = program.vert_code
FRAGMENT = program.frag_code

'''),


    ('Function chaining', '''
"""
Function chains are another essential component of shader composition,
allowing a list of functions to be executed in order.
"""

from vispy.visuals.shaders import ModularProgram, Function, FunctionChain

# Added a new hook to allow any number of functions to be executed
# after gl_Position is set.
vertex_shader = """
void vert_post_hook();

attribute vec4 position_a;

void main() {
    gl_Position = position_a;
    vert_post_hook();
}
"""

fragment_shader = """
void main() {
}
"""

program = ModularProgram(vertex_shader, fragment_shader)

# Add a function to flatten the z-position of the vertex
flatten = Function("""
    void flatten_func() {
        gl_Position.z = 0;
    }
    """)

# Add another function that copies an attribute to a varying
# for use in the fragment shader
read_color_attr = Function("""
    void $read_color_attr() {
        $output = $input;
    }
    """)

# ..and set two new program variables:
# (note that no value is needed for varyings)
read_color_attr['output'] = ('varying', 'vec4')
read_color_attr['input'] = ('attribute', 'vec4', 'color_a')


# Now create a chain that calls both functions in sequence
post_chain = FunctionChain('vert_post_hook', [flatten, read_color_attr])

program.set_hook('vert_post_hook', post_chain)


# obligatory: these variables are used to fill the text fields on the right.
program._compile()
VERTEX = program.vert_code
FRAGMENT = program.frag_code
'''),


    ('Function composition', '''
"""
Chains may also be used to generate a function composition where the return
value of each function call supplies the input to the next argument.
Thus, the original input is transformed in a series steps.

This is most commonly used for passing vertex positions through a composition
of transform functions.
"""

from vispy.visuals.shaders import ModularProgram, Function, FunctionChain


vertex_shader = """
vec4 transform_chain(vec4);

attribute vec4 position_a;

void main() {
    gl_Position = transform_chain(position_a);
}
"""

fragment_shader = """
void main() {
}
"""

program = ModularProgram(vertex_shader, fragment_shader)

flatten = Function("""
    vec4 flatten_func(vec4 pos) {
        pos.z = 0;
        pos.w = 1;
        return pos;
    }
    """)

# Define a scaling function
scale = Function("""
    vec4 $scale_vertex(vec4 pos) {
        return pos * vec4($scale, 1);
    }
    """)
scale['scale'] = ('uniform', 'vec3', (2, 1, 1))

# Assigning a list of both functions to a program hook will gemerate a
# composition of functions:
program['transform_chain'] = [flatten, scale]

# Internally, this creates a FunctionChain:
# transform = FunctionChain('transform_chain', [flatten, scale])


# obligatory: these variables are used to fill the text fields on the right.
program._compile()
VERTEX = program.vert_code
FRAGMENT = program.frag_code

'''),


    ('Fragment shaders', '''
"""
Although the prior examples focused on vertex shaders, these concepts
apply equally well for fragment shaders.

However: fragment shaders have one limitation that makes them very
different--they lack attributes. In order to supply attribute data
to a fragment shader, we will need to introduce some supporting code
to the vertex shader.
"""

from vispy.visuals.shaders import (ModularProgram, Function, FunctionChain)
from vispy.gloo import VertexBuffer
import numpy as np

# we require a void hook in the vertex shader that can be used
# to attach supporting code for the fragment shader.
vertex_shader = """
void vert_post_hook();

attribute vec4 position_a

void main() {
    gl_Position = position_a;
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

program = ModularProgram(vertex_shader, fragment_shader)

# First, define a simple fragment color function and bind it to a varying
# input:
frag_func = Function("vec4 $frag_color_input() { return $f_input; }")
frag_func['f_input'] = ('varying', 'vec4')

# Attach to the program
program['fragment_color'] = frag_func

# Next, we need a vertex shader function that will supply input
# to the varying.
vert_func = Function("void $vert_color_input() { $v_output = $v_input; }")
colors = VertexBuffer(np.array([[1,1,1,1]], dtype=np.float32))
vert_func['v_input'] = ('attribute', 'vec4', colors)

# to ensure both the vertex function output and the fragment function input
# are attached to the same varying, we use the following syntax:
vert_func['v_output'] = frag_func['f_input']

# and attach this to the vertex shader
program['vert_post_hook'] = vert_func


# obligatory: these variables are used to fill the text fields on the right.
program._compile()
VERTEX = program.vert_code
FRAGMENT = program.frag_code
'''),


    ('Sub-hooks', '''
"""
"""

from vispy.visuals.shaders import (ModularProgram, Function, FunctionChain)
from vispy.gloo import VertexBuffer
import numpy as np

vertex_shader = """
void vert_post_hook();

void main() {
    gl_Position = vec4(0,0,0,0);
    vert_post_hook();
}
"""

fragment_shader = """
void main() {
}
"""

program = ModularProgram(vertex_shader, fragment_shader)

# Create a function that calls another function
vert_func = Function("""
void $vert_func() {
    $some_other_function();
}
""")


# Create the second function:
other_func = Function("""
void $other_func() {
    gl_Position.w = 1;
}
""")

# Assign other_func to the anonymous function call in vert_func:
vert_func['some_other_function'] = other_func

# The name assigned to other_func will be inserted in place of
# the function call in vert_func

program['vert_post_hook'] = vert_func

# obligatory: these variables are used to fill the text fields on the right.
program._compile()
VERTEX = program.vert_code
FRAGMENT = program.frag_code
'''),


]


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
for i in range(3):
    editor.zoomOut()
    vertex.zoomOut()
    fragment.zoomOut()

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

example_menu = menubar.addMenu('Load example..')
for i, preset in enumerate(presets):
    name = preset[0]
    action = example_menu.addAction("%d. %s" % (i, name),
                                    mk_load_callback(name))

next_action = menubar.addAction("Next example", load_next)

win.show()
win.resize(1800, 1100)
hsplit.setSizes([900, 900])

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
    except Exception:
        vert = traceback.format_exc()
        frag = ""
        tb = sys.exc_info()[2]
        while tb is not None:
            #print(tb.tb_lineno, tb.tb_frame.f_code.co_filename)
            try:
                if tb.tb_frame.f_code.co_filename == '<string>':
                    editor.set_marker(tb.tb_lineno-1)
            except Exception:
                pass
            tb = tb.tb_next

    vertex.setText(vert)
    fragment.setText(frag)

editor.textChanged.connect(update)
update()

if __name__ == '__main__':
    app.exec_()
