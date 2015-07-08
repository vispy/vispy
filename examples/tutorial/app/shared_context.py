# -*- coding: utf-8 -*-
# vispy: testskip
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
This is a very simple example that demonstrates using a shared context
between two Qt widgets.
"""

# XXX THIS IS CURRENTLY BROKEN

from PyQt4 import QtGui, QtCore  # can also use pyside
from functools import partial

from vispy.app import Timer
from vispy.scene.visuals import Text
from vispy.scene.widgets import ViewBox
from vispy.scene import SceneCanvas


def on_resize(canvas, vb, event):
    vb.pos = 1, 1
    vb.size = (canvas.size[0] - 2, canvas.size[1] - 2)


class Window(QtGui.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        box = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight, self)
        self.resize(500, 200)
        self.setLayout(box)

        self.canvas_0 = SceneCanvas(bgcolor='w')
        self.vb_0 = ViewBox(parent=self.canvas_0.scene, bgcolor='r')
        self.vb_0.camera.rect = -1, -1, 2, 2
        self.canvas_0.events.initialize.connect(self.on_init)
        self.canvas_0.events.resize.connect(partial(on_resize,
                                                    self.canvas_0,
                                                    self.vb_0))
        box.addWidget(self.canvas_0.native)

        # pass the context from the first canvas to the second
        self.canvas_1 = SceneCanvas(bgcolor='w', shared=self.canvas_0.context)
        self.vb_1 = ViewBox(parent=self.canvas_1.scene, bgcolor='b')
        self.vb_1.camera.rect = -1, -1, 2, 2
        self.canvas_1.events.resize.connect(partial(on_resize,
                                                    self.canvas_1,
                                                    self.vb_1))
        box.addWidget(self.canvas_1.native)

        self.tick_count = 0
        self.timer = Timer(interval=1., connect=self.on_timer, start=True)
        self.setWindowTitle('Shared contexts')
        self.show()

    def on_init(self, event):
        self.text = Text('Initialized', font_size=40.,
                         anchor_x='left', anchor_y='top',
                         parent=[self.vb_0.scene, self.vb_1.scene])

    def on_timer(self, event):
        self.tick_count += 1
        self.text.text = 'Tick #%s' % self.tick_count
        self.canvas_0.update()
        self.canvas_1.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        elif event.key() == QtCore.Qt.Key_F11:
            self.showNormal() if self.isFullScreen() else self.showFullScreen()

if __name__ == '__main__':
    qt_app = QtGui.QApplication([])
    ex = Window()
    qt_app.exec_()
