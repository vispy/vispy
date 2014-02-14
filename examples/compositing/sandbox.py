from PyQt4 import QtCore
from PyQt4.QtGui import *
import traceback

from editor import Editor

app = QApplication([])

win = QWidget()
layout = QGridLayout()
win.setLayout(layout)

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

win.show()
win.resize(1000,800)

editor.setText('''
from vispy.shaders.composite import CompositeProgram

vertex_shader = """
void post_hook();

void main() {
    post_hook();
}

"""


fragment_shader = """

void main() {

}

"""


program = CompositeProgram(vertex_shader, fragment_shader)

# obligatory: these variables are used to fill the text fields on the right.
VERTEX, FRAGMENT = program._generate_code()
''')


def update():
    code = editor.text()
    local = {}
    glob = {}
    try:
        exec(code, local, glob)
        vert = glob['VERTEX']
        frag = glob['FRAGMENT']
    except:
        vert = traceback.format_exc()
        frag = ""
        
    vertex.setText(vert)
    fragment.setText(frag)
    
editor.textChanged.connect(update)
update()    
    
app.exec_()
