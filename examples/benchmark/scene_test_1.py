# -*- coding: utf-8 -*-
# vispy: testskip
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Compare an optimal pan/zoom implementation to the same functionality
provided by scenegraph.

Use --vispy-cprofile to see an overview of time spent in all functions.
Use util.profiler and --vispy-profile=ClassName.method_name for more directed
profiling measurements.
"""
import numpy as np
import math

from vispy import gloo, app, scene
from vispy.visuals import Visual
from vispy.visuals.shaders import Function, Variable
from vispy.visuals.transforms import TransformSystem, BaseTransform
from vispy.util.profiler import Profiler


class PanZoomTransform(BaseTransform):
    glsl_map = """
        vec4 pz_transform_map(vec4 pos) {
            return vec4($zoom * (pos.xy + $pan), 0., 1.);
        }
    """

    glsl_imap = """
        vec4 pz_transform_imap(vec2 pos) {
            return vec4(pos / $zoom - $pan, 0, 1);
        }
    """

    Linear = True
    Orthogonal = True
    NonScaling = False
    Isometric = False

    def __init__(self):
        super(PanZoomTransform, self).__init__()
        self._pan = None
        self._zoom = None

    @property
    def pan(self):
        if isinstance(self._pan, Variable):
            return np.array(self._pan.value, dtype=np.float32)
        else:
            raise NotImplementedError()

    @pan.setter
    def pan(self, value):
        if isinstance(value, Variable):
            self._pan = value
            self._shader_map['pan'] = self._pan
        elif isinstance(self._pan, Variable):
            self._pan.value = value
        else:
            raise NotImplementedError()

    @property
    def zoom(self):
        if isinstance(self._zoom, Variable):
            return np.array(self._zoom.value, dtype=np.float32)
        else:
            raise NotImplementedError()

    @zoom.setter
    def zoom(self, value):
        if isinstance(value, Variable):
            self._zoom = value
            self._shader_map['zoom'] = self._zoom
        elif isinstance(self._zoom, Variable):
            self._zoom.value = value
        else:
            raise NotImplementedError()

    def map(self, coords):
        if not isinstance(coords, np.ndarray):
            coords = np.array(coords)
        return self.zoom[None, :] * (coords + self.pan[None, :])

    def imap(self, coords):
        if not isinstance(coords, np.ndarray):
            coords = np.array(coords)
        return (coords / self.zoom[None, :]) - self.pan[None, :]


class PanZoomCanvas(app.Canvas):
    def __init__(self, **kwargs):
        super(PanZoomCanvas, self).__init__(keys='interactive', **kwargs)
        self._visuals = []

        self._pz = PanZoomTransform()
        self._pz.pan = Variable('uniform vec2 u_pan', (0, 0))
        self._pz.zoom = Variable('uniform vec2 u_zoom', (1, 1))

        self.width, self.height = self.size
        self.context.set_viewport(0, 0, self.physical_size[0],
                                  self.physical_size[1])
        self.context.set_state(clear_color='black', blend=True,
                               blend_func=('src_alpha', 'one_minus_src_alpha'))

        self._tr = TransformSystem(self)
        self.show()

    def on_resize(self, event):
        self.width, self.height = event.size
        self.context.set_viewport(0, 0, event.physical_size[0],
                                  event.physical_size[1])

    def _normalize(self, x_y):
        x, y = x_y
        w, h = float(self.width), float(self.height)
        return x/(w/2.)-1., y/(h/2.)-1.

    def bounds(self):
        pan_x, pan_y = self._pz.pan
        zoom_x, zoom_y = self._pz.zoom
        xmin = -1 / zoom_x - pan_x
        xmax = +1 / zoom_x - pan_x
        ymin = -1 / zoom_y - pan_y
        ymax = +1 / zoom_y - pan_y
        return (xmin, ymin, xmax, ymax)

    def on_mouse_move(self, event):
        if event.is_dragging and not event.modifiers:
            x0, y0 = self._normalize(event.press_event.pos)
            x1, y1 = self._normalize(event.last_event.pos)
            x, y = self._normalize(event.pos)
            dx, dy = x - x1, -(y - y1)
            button = event.press_event.button

            pan_x, pan_y = self._pz.pan
            zoom_x, zoom_y = self._pz.zoom

            if button == 1:
                self._pz.pan = (pan_x + dx/zoom_x,
                                pan_y + dy/zoom_y)
            elif button == 2:
                zoom_x_new, zoom_y_new = (zoom_x * math.exp(2.5 * dx),
                                          zoom_y * math.exp(2.5 * dy))
                self._pz.zoom = (zoom_x_new, zoom_y_new)
                self._pz.pan = (pan_x - x0 * (1./zoom_x - 1./zoom_x_new),
                                pan_y + y0 * (1./zoom_y - 1./zoom_y_new))
            self.update()

    def on_mouse_wheel(self, event):
        prof = Profiler()  # noqa
        if not event.modifiers:
            dx = np.sign(event.delta[1])*.05
            x0, y0 = self._normalize(event.pos)
            pan_x, pan_y = self._pz.pan
            zoom_x, zoom_y = self._pz.zoom
            zoom_x_new, zoom_y_new = (zoom_x * math.exp(2.5 * dx),
                                      zoom_y * math.exp(2.5 * dx))
            self._pz.zoom = (zoom_x_new, zoom_y_new)
            self._pz.pan = (pan_x - x0 * (1./zoom_x - 1./zoom_x_new),
                            pan_y + y0 * (1./zoom_y - 1./zoom_y_new))
            self.update()

    def on_key_press(self, event):
        if event.key == 'R':
            self._pz.zoom = (1., 1.)
            self._pz.pan = (0., 0.)
            self.update()

    def add_visual(self, name, value):
        value.shared_program.vert['transform'] = self._pz
        value.events.update.connect(self.update)
        self._visuals.append(value)

    def __setattr__(self, name, value):
        if isinstance(value, Visual):
            self.add_visual(name, value)
        super(PanZoomCanvas, self).__setattr__(name, value)

    @property
    def visuals(self):
        return self._visuals

    def on_draw(self, event):
        prof = Profiler()
        self.context.clear()
        for visual in self.visuals:
            visual.draw()
            prof('draw visual')


X_TRANSFORM = """
float get_x(float x_index) {
    // 'x_index' is between 0 and nsamples.
    return -1. + 2. * x_index / (float($nsamples) - 1.);
}
"""

Y_TRANSFORM = """
float get_y(float y_index, float sample) {
    // 'y_index' is between 0 and nsignals.
    float a = float($scale) / float($nsignals);
    float b = -1. + 2. * (y_index + .5) / float($nsignals);

    return a * sample + b;
}
"""

DISCRETE_CMAP = """
vec3 get_color(float index) {
    float x = (index + .5) / float($ncolors);
    return texture2D($colormap, vec2(x, .5)).rgb;
}
"""


class SignalsVisual(Visual):
    VERTEX_SHADER = """
    attribute float a_position;

    attribute vec2 a_index;
    varying vec2 v_index;

    uniform float u_nsignals;
    uniform float u_nsamples;

    void main() {
        vec4 position = vec4($get_x(a_index.y),
                             $get_y(a_index.x, a_position), 0., 1.);
        gl_Position = $transform(position);

        v_index = a_index;
    }
    """

    FRAGMENT_SHADER = """
    varying vec2 v_index;

    void main() {
        gl_FragColor = vec4($get_color(v_index.x), 1.);

        // Discard vertices between two signals.
        if ((fract(v_index.x) > 0.))
            discard;
    }
    """

    def __init__(self, data):
        Visual.__init__(self, self.VERTEX_SHADER, self.FRAGMENT_SHADER)

        nsignals, nsamples = data.shape
        # nsamples, nsignals = data.shape

        self._data = data

        a_index = np.c_[np.repeat(np.arange(nsignals), nsamples),
                        np.tile(np.arange(nsamples), nsignals)
                        ].astype(np.float32)

        # Doesn't seem to work nor to be very efficient.
        # indices = nsignals * np.arange(nsamples)
        # indices = indices[None, :] + np.arange(nsignals)[:, None]
        # indices = indices.flatten().astype(np.uint32)
        # self._ibuffer = gloo.IndexBuffer(indices)

        self._buffer = gloo.VertexBuffer(data.reshape(-1, 1))
        self.shared_program['a_position'] = self._buffer
        self.shared_program['a_index'] = a_index

        x_transform = Function(X_TRANSFORM)
        x_transform['nsamples'] = nsamples
        self.shared_program.vert['get_x'] = x_transform

        y_transform = Function(Y_TRANSFORM)
        y_transform['scale'] = Variable('uniform float u_signal_scale', 1.)
        y_transform['nsignals'] = nsignals
        self.shared_program.vert['get_y'] = y_transform
        self._y_transform = y_transform

        colormap = Function(DISCRETE_CMAP)
        rng = np.random.RandomState(0)
        cmap = rng.uniform(size=(1, nsignals, 3),
                           low=.5, high=.9).astype(np.float32)
        tex = gloo.Texture2D((cmap * 255).astype(np.uint8))
        colormap['colormap'] = Variable('uniform sampler2D u_colormap', tex)
        colormap['ncolors'] = nsignals
        self.shared_program.frag['get_color'] = colormap
        self._draw_mode = 'line_strip'
        self.set_gl_state('translucent', depth_test=False)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self._buffer.set_subdata(value.reshape(-1, 1))
        self.update()

    @property
    def signal_scale(self):
        return self._y_transform['scale'].value

    @signal_scale.setter
    def signal_scale(self, value):
        self._y_transform['scale'].value = value
        self.update()

    def _prepare_draw(self, view=None):
        """This method is called immediately before each draw.

        The *view* argument indicates which view is about to be drawn.
        """
        pass


Signals = scene.visuals.create_visual_node(SignalsVisual)


if __name__ == '__main__':
    data = np.random.normal(size=(128, 1000)).astype(np.float32)

    pzcanvas = PanZoomCanvas(position=(400, 300), size=(800, 600),
                             title="PanZoomCanvas", vsync=False)
    visual = SignalsVisual(data)
    pzcanvas.add_visual('signal', visual)

    scanvas = scene.SceneCanvas(show=True, keys='interactive',
                                title="SceneCanvas", vsync=False)
    view = scanvas.central_widget.add_view('panzoom')
    svisual = Signals(data, parent=view.scene)
    view.camera.set_range([-0.9, 0.9], [-0.9, 0.9])

    import sys
    if sys.flags.interactive != 1:
        app.run()
