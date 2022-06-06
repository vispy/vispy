"""
Embed VisPy into Qt
-------------------

Display VisPy visualizations in a PySide2 application.

"""

import sys

import numpy as np
from PySide2 import QtWidgets, QtGui

from vispy.scene import SceneCanvas, visuals
from vispy.app import use_app

IMAGE_SHAPE = (600, 800)
CANVAS_SIZE = (800, 600)


class MyMainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        central_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout()

        self._controls = Controls()
        main_layout.addWidget(self._controls)
        self._canvas_wrapper = CanvasWrapper()
        main_layout.addWidget(self._canvas_wrapper.canvas.native)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)


class Controls(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout()
        self.colormap_label = QtWidgets.QLabel("Image Colormap:")
        layout.addWidget(self.colormap_label)
        self.colormap_chooser = QtWidgets.QComboBox()
        self.colormap_chooser.addItems(["viridis", "reds", "blues"])
        layout.addWidget(self.colormap_chooser)

        self.line_color_label = QtWidgets.QLabel("Line color:")
        layout.addWidget(self.line_color_label)
        self.line_color_chooser = QtWidgets.QComboBox()
        self.line_color_chooser.addItems(["black", "red", "blue"])
        layout.addWidget(self.line_color_chooser)

        layout.addStretch(1)
        self.setLayout(layout)


class CanvasWrapper:
    def __init__(self):
        self.canvas = SceneCanvas(size=CANVAS_SIZE, bgcolor="cyan")
        self.view = self.canvas.central_widget.add_view()
        image_data = _generate_random_image_data(IMAGE_SHAPE)
        self.image = visuals.Image(
            image_data,
            texture_format="auto",
            cmap="viridis",
            parent=self.view.scene,
        )


def _generate_random_image_data(shape, dtype=np.float32):
    rng = np.random.default_rng()
    data = rng.random(shape, dtype=dtype)
    return data


def main():
    app = use_app("pyside2")
    app.create()
    win = MyMainWindow()
    win.show()
    app.run()


if __name__ == "__main__":
    sys.exit(main())
