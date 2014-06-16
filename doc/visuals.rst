==============
Visual objects
==============

VisPy provides a library of drawable objects that are intended to encapsulate 
simple graphic objects such as lines, meshes, points, volumes, 2D shapes, 
images, text, etc. More complex visuals are also available that simply combine
multiple simpler visuals, such as plot axes, ...

Most visuals consist of a base :class:`Visual` instance combined with multiple 
:class:`VisualComponent` instances that customize the visual's output. The
Visual itself implements a `paint()` method that decides which GL primitive 
type to draw (point, line, tri) and provides the user with an interface for 
setting and modifying the data to be displayed.

In contrast, most of the details of determining how the visual will appear on 
screen are handled by *components*. These configure the visual to allow 
different types of data input, vertex transformations, and combinations of 
coloring functions. 

For example, a 3D mesh visual may have a variety of components that:
    
* Determine the input data source (1D, 2D, or 3D vertex buffer; texture
  lookup; function generation; etc.)
* Define the transformation(s) that map to the coordinate systems relevant to 
  the visual
* Determine the input color source (RGBA, RGB, LA, L, colormap, lookup table,
  etc.)
* Determine the normal vector (3D vector, bump map, shape generation function,
  etc.)
* Make modifications to the color based on normals, textures, procedural rules,
  etc. 
  
Most components can be stacked together to create arbitrary combinations. 
Behind the scenes, the Visual system handles constructing shader code and
activating buffers associated with the individual components. The visual itself
only provides a bare GLSL skeleton program; it is up to the components to 
fill out the details of how the program will behave.


Overview of Visual and VisualComponent interactions
===================================================








.. automodule:: vispy.visuals


Base class
==========

.. autoclass:: vispy.visuals.Visual
    :members:


 