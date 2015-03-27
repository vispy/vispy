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


### Introduction to the rendering pipeline


### First GLSL shaders


### GPU-based animations in GLSL

