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
from vispy import app, gloo

# Create a canvas with common key bindings for interactive use.
canvas = app.Canvas(keys='interactive')

# Use this decorator to register event handlers.
@canvas.connect
def on_draw(event):
    # The window needs to be cleared at every draw.
    gloo.clear('deepskyblue')

canvas.show()
```

### Introduction to the rendering pipeline

The rendering pipeline defines how data is processed on the GPU for rendering.

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

Finally, `program.draw()` renders the data using the specified primitive type. Here, the line_strip primitive type tells the GPU to run through all vertices (as returned by the vertex buffer) and to draw a line segment from one point to the next. If there are `n` points, there will be `n-1` line segments.

Other primitive types include points and triangles, with several ways of generating lines or triangles from a list of vertices.

In addition, an index buffer may be provided. An index buffer contains indices pointing to the vertex buffers. Using an index buffer would allow us to reuse any vertex multiple times during the primitive assembly stage. For example, when rendering a cube with a triangles primitive type (one triangle is generated for every triplet of points), we could use a vertex buffer with 8 data points and an index buffer with 36 indices (3 points per triangle, 2 triangles per face, 6 faces).




### First GLSL shaders




### GPU-based animations in GLSL


