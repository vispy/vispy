# -*- coding: utf-8 -*-
# vispy: gallery 10
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import sys
import numpy as np

from vispy import app, gloo, visuals
from vispy.visuals.filters import Clipper, ColorFilter
from vispy.visuals.shaders import MultiProgram
from vispy.visuals.collections import PointCollection
from vispy.visuals.transforms import STTransform

from vispy.scene import SceneCanvas
from vispy.scene.visuals import create_visual_node


class LineVisual(visuals.Visual):
    """Example of a very simple GL-line visual.

    This shows the minimal set of methods that need to be reimplemented to 
    make a new visual class.

    """

    def __init__(self, pos=None, color=(1, 1, 1, 1)):
        vcode = """
        attribute vec2 a_pos;
        
        void main() {
            gl_Position = $transform(vec4(a_pos, 0., 1.)); 
            gl_PointSize = 10.;
        }
        """

        fcode = """
        void main() {
            gl_FragColor = $color;
        }
        """

        visuals.Visual.__init__(self, vcode=vcode, fcode=fcode)

        self.pos_buf = gloo.VertexBuffer()

        # The Visual superclass contains a MultiProgram, which is an object
        # that behaves like a normal shader program (you can assign shader
        # code, upload values, set template variables, etc.) but internally
        # manages multiple ModularProgram instances, one per view.

        # The MultiProgram is accessed via the `shared_program` property, so
        # the following modifications to the program will be applied to all 
        # views:
        self.shared_program['a_pos'] = self.pos_buf
        self.shared_program.frag['color'] = color

        self._need_upload = False

        # Visual keeps track of draw mode, index buffer, and GL state. These
        # are shared between all views.
        self._draw_mode = 'line_strip'
        self.set_gl_state('translucent', depth_test=False)

        if pos is not None:
            self.set_data(pos)

    def set_data(self, pos):
        self._pos = pos
        self._need_upload = True

    def _prepare_transforms(self, view=None):
        view.view_program.vert['transform'] = view.transforms.get_transform()

    def _prepare_draw(self, view=None):
        """This method is called immediately before each draw.

        The *view* argument indicates which view is about to be drawn.
        """
        if self._need_upload:
            # Note that pos_buf is shared between all views, so we have no need
            # to use the *view* argument in this example. This will be true
            # for most visuals.
            self.pos_buf.set_data(self._pos)
            self._need_upload = False


class PointVisual(LineVisual):
    """Another simple visual class. 

    Due to the simplicity of these example classes, it was only necessary to
    subclass from LineVisual and set the draw mode to 'points'. A more
    fully-featured PointVisual class might not follow this approach.
    """

    def __init__(self, pos=None, color=(1, 1, 1, 1)):
        LineVisual.__init__(self, pos, color)
        self._draw_mode = 'points'


class PlotLineVisual(visuals.CompoundVisual):
    """An example compound visual that draws lines and points.

    To the user, the compound visual behaves exactly like a normal visual--it
    has a transform system, draw() and bounds() methods, etc. Internally, the
    compound visual automatically manages proxying these transforms and methods
    to its sub-visuals.
    """

    def __init__(self, pos=None, line_color=(1, 1, 1, 1),
                 point_color=(1, 1, 1, 1)):
        self._line = LineVisual(pos, color=line_color)
        self._point = PointVisual(pos, color=point_color)
        visuals.CompoundVisual.__init__(self, [self._line, self._point])


class PointCollectionVisual(visuals.Visual):
    """Thin wrapper around a point collection.

    Note: This is currently broken!
    """

    def __init__(self):
        prog = MultiProgram(vcode='', fcode='')
        self.points = PointCollection("agg", color="shared", program=prog)
        visuals.Visual.__init__(self, program=prog)

    def _prepare_draw(self, view):
        if self.points._need_update:
            self.points._update()
        self._draw_mode = self.points._mode
        self._index_buffer = self.points._indices_buffer

    def append(self, *args, **kwargs):
        self.points.append(*args, **kwargs)

    def _prepare_transforms(self, view=None):
        pass

    @property
    def color(self):
        return self.points['color']

    @color.setter
    def color(self, c):
        self.points['color'] = c


class PanZoomTransform(STTransform):
    def __init__(self, canvas=None, aspect=None, **kwargs):
        self._aspect = aspect
        self.attach(canvas)
        STTransform.__init__(self, **kwargs)

    def attach(self, canvas):
        """ Attach this tranform to a canvas """
        self._canvas = canvas
        canvas.events.mouse_wheel.connect(self.on_mouse_wheel)
        canvas.events.mouse_move.connect(self.on_mouse_move)

    def on_mouse_move(self, event):
        if event.is_dragging:
            dxy = event.pos - event.last_event.pos
            button = event.press_event.button

            if button == 1:
                self.move(dxy)
            elif button == 2:
                center = event.press_event.pos
                if self._aspect is None:
                    self.zoom(np.exp(dxy * (0.01, -0.01)), center)
                else:
                    s = dxy[1] * -0.01
                    self.zoom(np.exp(np.array([s, s])), center)

    def on_mouse_wheel(self, event):
        self.zoom(np.exp(event.delta * (0.01, -0.01)), event.pos)


canvas = app.Canvas(keys='interactive', size=(900, 600), show=True, 
                    title="Visual Canvas")
pos = np.random.normal(size=(1000, 2), loc=0, scale=50).astype('float32')
pos[0] = [0, 0]

# Make a line visual
line = LineVisual(pos=pos)
line.transforms.canvas = canvas
line.transform = STTransform(scale=(2, 1), translate=(20, 20))
panzoom = PanZoomTransform(canvas)
line.transforms.scene_transform = panzoom
panzoom.changed.connect(lambda ev: canvas.update())

# Attach color filter to all views (current and future) of the visual
line.attach(ColorFilter((1, 1, 0.5, 0.7)))

# Attach a clipper just to this view. The Clipper filter requires a
# transform that maps from the framebuffer coordinate system to the 
# clipping coordinates.
tr = line.transforms.get_transform('framebuffer', 'canvas')
line.attach(Clipper((20, 20, 260, 260), transform=tr), view=line)

# Make a view of the line that will draw its shadow
shadow = line.view()
shadow.transforms.canvas = canvas
shadow.transform = STTransform(scale=(2, 1), translate=(25, 25))
shadow.transforms.scene_transform = panzoom
shadow.attach(ColorFilter((0, 0, 0, 0.6)), view=shadow)
tr = shadow.transforms.get_transform('framebuffer', 'canvas')
shadow.attach(Clipper((20, 20, 260, 260), transform=tr), view=shadow)

# And make a second view of the line with different clipping bounds
view = line.view()
view.transforms.canvas = canvas
view.transform = STTransform(scale=(2, 0.5), translate=(450, 150))
tr = view.transforms.get_transform('framebuffer', 'canvas')
view.attach(Clipper((320, 20, 260, 260), transform=tr), view=view)

# Make a compound visual
plot = PlotLineVisual(pos, (0.5, 1, 0.5, 0.2), (0.5, 1, 1, 0.3))
plot.transforms.canvas = canvas
plot.transform = STTransform(translate=(80, 450), scale=(1.5, 1))
tr = plot.transforms.get_transform('framebuffer', 'canvas')
plot.attach(Clipper((20, 320, 260, 260), transform=tr), view=plot)

# And make a view on the compound 
view2 = plot.view()
view2.transforms.canvas = canvas
view2.transform = STTransform(scale=(1.5, 1), translate=(450, 400))
tr = view2.transforms.get_transform('framebuffer', 'canvas')
view2.attach(Clipper((320, 320, 260, 260), transform=tr), view=view2)

# And a shadow for the view
shadow2 = plot.view()
shadow2.transforms.canvas = canvas
shadow2.transform = STTransform(scale=(1.5, 1), translate=(455, 405))
shadow2.attach(ColorFilter((0, 0, 0, 0.6)), view=shadow2)
tr = shadow2.transforms.get_transform('framebuffer', 'canvas')
shadow2.attach(Clipper((320, 320, 260, 260), transform=tr), view=shadow2)

# Example of a collection visual
collection = PointCollectionVisual()
collection.transforms.canvas = canvas
collection.transform = STTransform(translate=(750, 150))
collection.append(np.random.normal(loc=0, scale=20, size=(10000, 3)), 
                  itemsize=5000)
collection.color = (1, 0.5, 0.5, 1), (0.5, 0.5, 1, 1)

shadow3 = collection.view()
shadow3.transforms.canvas = canvas
shadow3.transform = STTransform(scale=(1, 1), translate=(752, 152))
shadow3.attach(ColorFilter((0, 0, 0, 0.6)), view=shadow3)
# tr = shadow3.transforms.get_transform('framebuffer', 'canvas')
# shadow3.attach(Clipper((320, 320, 260, 260), transform=tr), view=shadow2)

order = [shadow, line, view, plot, shadow2, view2, shadow3, collection]


@canvas.connect
def on_draw(event):
    canvas.context.clear((0.3, 0.3, 0.3, 1.0))
    for v in order:
        v.draw()


def on_resize(event):
    # Set canvas viewport and reconfigure visual transforms to match.
    vp = (0, 0, canvas.physical_size[0], canvas.physical_size[1])
    canvas.context.set_viewport(*vp)
    for v in order:
        v.transforms.configure(canvas=canvas, viewport=vp)
canvas.events.resize.connect(on_resize)
on_resize(None)

Line = create_visual_node(LineVisual)
canvas2 = SceneCanvas(keys='interactive', title='Scene Canvas', show=True)
v = canvas2.central_widget.add_view(margin=10)
v.border_color = (1, 1, 1, 1)
v.bgcolor = (0.3, 0.3, 0.3, 1)
v.camera = 'panzoom'
line2 = Line(pos, parent=v.scene)


def mouse(ev):
    print(ev)

v.events.mouse_press.connect(mouse)

if __name__ == '__main__':
    if sys.flags.interactive != 1:
        app.run()
