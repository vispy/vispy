# VisPy user guide

Welcome to the VisPy user guide!

## Introduction to VisPy

VisPy aims at offering high-quality, high-performance scientific visualization facilities in Python. In development since 2013, VisPy represents a joint effort of four developers who had independently worked on OpenGL-based visualization libraries. With the low-level foundations being layed out, the plotting API of VisPy is now usable by all scientists. No knowledge of OpenGL is required for most plotting use-cases.

There are three levels with which VisPy can be used:

* 3. **Scientific plotting interface**: most use-cases
* 2. **Scene graph**: advanced use-cases
* 1. **Pythonic OpenGL (gloo)**: optimal performance on highly-specific use-cases

Level 3 is implemented on top of level 2 which is itself implemented on top of level 1.


## Interactive scientific plots

Several common plotting functions are available in `vispy.plot`. The plotting interface is still in extensive development and the API might be subject to changes in future versions.

### Line plot

TODO

```python
import vispy.plot as vp
vp.plot(x, y)
```

### Scatter plot

TODO


### Images

TODO


### Surface plot

TODO


### matplotlib and VisPy

There is an experimental matplotlib-to-VisPy converter in `vispy.mpl_plot`.

```python
import vispy.mpl_plot as plt
plt.plot(x, y)  # this is a normal matplotlib API call
plt.draw()  # replace the normal matplotlib plt.show() by this
```

It still doesn't work in all cases, but eventually it will.


## The scene graph

The scene graph targets users who have more advanced needs than what `vispy.plot` provides. The scene graph is a dynamic graph where nodes are visual elements, and edges represent relative transformations. The scene graph therefore encodes the positions of all visual elements in the scene.

TODO

### Displaying an empty window

* Changing the background color


### Displaying visuals



### Handling transforms


## Pythonic OpenGL (gloo)

OpenGL is a low-level graphics API that gives access to the **Graphics Processing Unit (GPU)** for high-performance real-time 2D/3D visualization. It is a complex API, but VisPy implements a user-friendly and Pythonic interface that makes it considerably easier to use OpenGL.

### Creating a window

First, let's see how to create a window:

```python
from vispy import app, gloo

# Create a canvas with common key bindings for interactive use.
canvas = app.Canvas(keys='interactive')

# Use this decorator to register event handlers.
@canvas.connect
def on_draw(event):
    # The window needs to be cleared at every draw.
    gloo.clear('deepskyblue')

canvas.show()
app.run()  # Not necessary in interactive mode.
```


### Event handlers

Here are the main events. Every function accepts an `event` object as argument. The attributes of this object depend on the event, you will find them in the API documentation.

* `on_resize`: when the window is resized. Use-cases: set the viewport, reorganize the layout of the visuals.
* `on_draw`: when the scene is drawn.
* `on_mouse_press`: when the mouse is pressed. Attributes:
    * `event.buttons`: list of pressed buttons (1, 2, or 3)
    * `events.pos` (in window coordinates)
* `on_mouse_release`: when the mouse is released after it has been pressed.
* `on_mouse_move`: when the mouse moves. The `event.is_dragging` attribute can be used to handle drag and drop events.
* `on_mouse_wheel`: when the mouse wheel changes. Attributes:
    * `event.delta[1]`: amount of scroll in the vertical direction.
* `on_key_press`: when a key is pressed. Attributes:
    * `event.key`: `Key` instance.
    * `event.text`: string with the key pressed.
* `on_key_release`: when a key is released.

Here is an example:

```python
import numpy as np
from vispy import app, gloo

canvas = app.Canvas(keys='interactive')

@canvas.connect
def on_mouse_move(event):
    x, y = event.pos  # Position of the cursor in window coordinates.
    w, h = canvas.size  # Size of the window (in pixels).
    
    # We update the background color when the mouse moves.
    r, b = np.clip([x / float(w), y / float(h)], 0, 1)
    gloo.clear((r, 0.0, b, 1.0))

    # This is used to refresh the window and trigger a draw event.
    canvas.update()

canvas.show()
app.run()
```

### Introduction to the rendering pipeline

Now that we can display windows, let's get started with OpenGL.

> This paragraph comes mostly from the [IPython Cookbook](https://ipython-books.github.io/featured-06/).

The **rendering pipeline** defines how data is processed on the GPU for rendering.

There are four major elements in the rendering pipeline of a given OpenGL program:

* **Data buffers** store numerical data on the GPU. The main types of buffers are **vertex buffers**, **index buffers**, and **textures**.

* **Variables** are available in the shaders. There are four major types of variables: **attributes**, **uniforms**, **varyings**, and **texture samplers**.

* **Shaders** are GPU programs written in a C-like language called OpenGL Shading Language (GLSL). The two main types of shaders are **vertex shaders** and **fragment shaders**.

* The **primitive type** defines the way data points are rendered. The main types are **points**, **lines*, and **triangles**.

Here is how the rendering pipeline works:

1. Data is sent on the GPU and stored in buffers.
2. The vertex shader processes the data in parallel and generates a number of 4D points in a normalized coordinate system (+/-1, +/-1). The fourth dimension is a homogeneous coordinate (generally 1).
3. Graphics primitives are generated from the data points returned by the vertex shader (primitive assembly and rasterization).
4. The fragment shader processes all primitive pixels in parallel and returns each pixel's color as RGBA components.

In `vispy.gloo`, a Program is created with the vertex and fragment shaders. Then, the variables declared in the shaders can be set with the syntax `program['varname'] = value`. When `varname` is an attribute variable, the value can just be a NumPy 2D array. In this array, every line contains the components of every data point.

Similarly, we could declare and set uniforms and textures in our program.

Finally, `program.draw()` renders the data using the specified primitive type (point, line, or triangle).

In addition, an index buffer may be provided. An index buffer contains indices pointing to the vertex buffers. Using an index buffer would allow us to reuse any vertex multiple times during the primitive assembly stage. For example, when rendering a cube with a triangles primitive type (one triangle is generated for every triplet of points), we could use a vertex buffer with 8 data points and an index buffer with 36 indices (3 points per triangle, 2 triangles per face, 6 faces).


### First GLSL shaders

Let's now write our first shaders. We will just display points in two dimensions. We will need the following components:

* A `(n, 2)` NumPy array with the 2D positions of the `n` points.
* A simple vertex shader performing no transformation at all on the point coordinates.
* A simple fragment shader returning a constant pixel color.

There is one attribute variable `a_position`. This `vec2` variable encodes the (x, y) coordinates of every point.

```python
from vispy import app, gloo
import numpy as np

vertex_shader = """
attribute vec2 a_position;
void main() {
    // gl_Position is the special return value of the vertex shader.
    // It is a vec4, so here we convert the vec2 position into 
    // a vec4. We set the third component to 0 because we're in 2D, and the 
    // fourth one to 1 (we don't need homogeneous coordinates here).
    gl_Position = vec4(a_position, 0.0, 1.0);

    // This is the size of the displayed points.
    gl_PointSize = 1.0;
}
"""

fragment_shader = """
void main() {
    // gl_FragColor is the special return value of the fragment shader.
    // It is a vec4 with rgba components. Here we just return the color blue.
    gl_FragColor = vec4(0.0, 0.0, 1.0, 1.0);
}
"""

# We create an OpenGL program with the vertex and fragment shader.
program = gloo.Program(vertex_shader, fragment_shader)

# We generate the x, y coordinates of the points.
position = .25 * np.random.randn(100000, 2)

# We set the a_position attribute to the position NumPy array.
# Every row in the array is one vertex. The vertex shader is called once per
# vertex, so once per row.
# WARNING: most GPUs only support float32 data (not float64).
program['a_position'] = position.astype(np.float32)

# We create a ccanvas.
canvas = app.Canvas(keys='interactive')

# We update the viewport when the window is resized.
@canvas.connect
def on_resize(event):
    width, height = event.size
    gloo.set_viewport(0, 0, width, height)

@canvas.connect
def on_draw(event):
    # We clear the window.
    gloo.clear('white')

    # We render the program with the 'points' mode. Every vertex is
    # rendered as a point.
    program.draw('points')

canvas.show()
app.run()
```


### GPU-based animations in GLSL

For optimal performance, interactivity and animations should be implemented on the GPU. Vertex positions can be updated in real-time on the GPU, which is used for panning and zooming for example. This is optimal because vertices are all processed in parallel on the GPU. Also, the fragment shader can be used for ray tracing, fractals, and volume rendering.

Here is a simple example where an animation is implemented on the GPU:

```python
from vispy import app, gloo
import numpy as np

# We manually tesselate an horizontal rectangle. We will use triangle strips.
n = 100
position = np.zeros((2*n, 2)).astype(np.float32)
position[:,0] = np.repeat(np.linspace(-1, 1, n), 2)
position[::2,1] = -.2
position[1::2,1] = .2
color = np.linspace(0., 1., 2 * n).astype(np.float32)

vertex_shader = """
const float M_PI = 3.14159265358979323846;

attribute vec2 a_position;
attribute float a_color;

// Varyings are used to passed values from the vertex shader to the fragment
// shader. The value at one pixel in the fragment shader is interpolated
// from the values at the neighboring pixels.
varying float v_color;
uniform float u_time;

void main (void) {
    // We implement the animation in the y coordinate.
    float x = a_position.x;
    float y = a_position.y + .1 * cos(2.0*M_PI*(u_time-.5*x));
    gl_Position = vec4(x, y, 0.0, 1.0);
    
    // We pass the color to the fragment shader.
    v_color = a_color;
}
"""

fragment_shader = """
uniform float u_time;
varying float v_color;
void main()
{
    gl_FragColor = vec4(1.0, v_color, 0.0, 1.0);
}
"""

# This is an alternative way to create a canvas: deriving from app.Canvas.
class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, keys='interactive')
        self.program = gloo.Program(vertex_shader, fragment_shader)
        self.program['a_position'] = gloo.VertexBuffer(position)
        self.program['a_color'] = gloo.VertexBuffer(color)
        self.program['u_time'] = 0.

        # We create a timer for the animation.
        self._timer = app.Timer('auto', connect=self.on_timer, start=True)

    def on_resize(self, event):
        width, height = event.size
        gloo.set_viewport(0, 0, width, height)

    def on_draw(self, event):
        gloo.clear(color=(0.0, 0.0, 0.0, 1.0))
        self.program.draw('triangle_strip')

    def on_timer(self, event):
        # We update theu_time uniform at every iteration.
        self.program['u_time'] = event.iteration * 1. / 60

        # This is used to refresh the window and trigger a draw event.
        self.update()

canvas = Canvas()
canvas.show()
app.run()
```
