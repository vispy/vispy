# -*- coding: utf-8 -*-
# vispy: testskip
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Demonstrate how to do offscreen rendering.
Possible use cases:

  * GPGPU without CUDA or OpenCL
  * creation of scripted animations
  * remote and Web backends

The method consists of:

  1. Not showing the canvas (show=False).
  2. Rendering to an FBO.
  3. Manually triggering a rendering pass with self.update().
  4. Retrieving the scene with _screenshot().
  5. Closing the app after the first rendering pass (if that's the intended
     scenario).

"""

from vispy import gloo
from vispy import app
from vispy.util.ptime import time
from vispy.gloo.util import _screenshot

# WARNING: doesn't work with Qt4 (update() does not call on_draw()??)
app.use_app('glfw')

vertex = """
attribute vec2 position;

void main()
{
    gl_Position = vec4(position, 0, 1.0);
}
"""

fragment = """
uniform vec2 resolution;
uniform vec2 center;
uniform float scale;
uniform int iter;

// Jet color scheme
vec4 color_scheme(float x) {
    vec3 a, b;
    float c;
    if (x < 0.34) {
        a = vec3(0, 0, 0.5);
        b = vec3(0, 0.8, 0.95);
        c = (x - 0.0) / (0.34 - 0.0);
    } else if (x < 0.64) {
        a = vec3(0, 0.8, 0.95);
        b = vec3(0.85, 1, 0.04);
        c = (x - 0.34) / (0.64 - 0.34);
    } else if (x < 0.89) {
        a = vec3(0.85, 1, 0.04);
        b = vec3(0.96, 0.7, 0);
        c = (x - 0.64) / (0.89 - 0.64);
    } else {
        a = vec3(0.96, 0.7, 0);
        b = vec3(0.5, 0, 0);
        c = (x - 0.89) / (1.0 - 0.89);
    }
    return vec4(mix(a, b, c), 1.0);
}

void main() {
    vec2 z, c;

    // Recover coordinates from pixel coordinates
    c.x = (gl_FragCoord.x / resolution.x - 0.5) * scale + center.x;
    c.y = (gl_FragCoord.y / resolution.y - 0.5) * scale + center.y;

    // Main Mandelbrot computation
    int i;
    z = c;
    for(i = 0; i < iter; i++) {
        float x = (z.x * z.x - z.y * z.y) + c.x;
        float y = (z.y * z.x + z.x * z.y) + c.y;

        if((x * x + y * y) > 4.0) break;
        z.x = x;
        z.y = y;
    }

    // Convert iterations to color
    float color = 1.0 - float(i) / float(iter);
    gl_FragColor = color_scheme(color);

}
"""


class Canvas(app.Canvas):
    def __init__(self, size=(600, 600)):
        # We hide the canvas upon creation.
        app.Canvas.__init__(self, show=False, size=size)
        self._t0 = time()
        # Texture where we render the scene.
        self._rendertex = gloo.Texture2D(shape=self.size + (4,))
        # FBO.
        self._fbo = gloo.FrameBuffer(self._rendertex,
                                     gloo.RenderBuffer(self.size))
        # Regular program that will be rendered to the FBO.
        self.program = gloo.Program(vertex, fragment)
        self.program["position"] = [(-1, -1), (-1, 1), (1, 1),
                                    (-1, -1), (1, 1), (1, -1)]
        self.program["scale"] = 3
        self.program["center"] = [-0.5, 0]
        self.program["iter"] = 300
        self.program['resolution'] = self.size
        # We manually draw the hidden canvas.
        self.update()

    def on_draw(self, event):
        # Render in the FBO.
        with self._fbo:
            gloo.clear('black')
            gloo.set_viewport(0, 0, *self.size)
            self.program.draw()
            # Retrieve the contents of the FBO texture.
            self.im = _screenshot((0, 0, self.size[0], self.size[1]))
        self._time = time() - self._t0
        # Immediately exit the application.
        app.quit()

if __name__ == '__main__':
    c = Canvas()
    size = c.size
    app.run()

    # The rendering is done, we get the rendering output (4D NumPy array)
    render = c.im
    print('Finished in %.1fms.' % (c._time*1e3))

    # Now, we display this image with matplotlib to check.
    import matplotlib.pyplot as plt
    plt.figure(figsize=(size[0]/100., size[1]/100.), dpi=100)
    plt.imshow(render, interpolation='none')
    plt.show()
