Roadmap
=======

Where do we see VisPy going in the future? What is development focused on?
What can users look forward to in upcoming VisPy major releases?
We try to answer these types of "big picture" questions below.
For shorter term issues and plans see the
`GitHub issue tracker <https://github.com/vispy/vispy/issues>`_.

Road to Version 1.0
-------------------

At the time of writing VisPy still doesn't have a 1.x version number despite
being used by hundreds of users from graduate students to industry. We believe
a 1.0 version should represent stability and feeling of completeness when it
comes to interfaces, performance, and functionality. We don't think we're there
yet, but we have ideas for what a 1.0 release might look like and we've
described it below.

Performance and Collections
^^^^^^^^^^^^^^^^^^^^^^^^^^^

One of the main reasons users come to VisPy (or so we've been told) is the
performance of visualizing **a lot** of data or visualizing data that updates
quickly. VisPy does a pretty good job covering users for these use cases, but
it can do better. The main areas that need improvement are:

1. ``SceneCanvas`` (`#1991 <https://github.com/vispy/vispy/issues/1991>`_):
   In other visualization spaces, a scene graph performs optimizations
   for when and how components are drawn. If multiple pieces of a visualization
   have shared logic, let's not recompile or re-communicate things to the GPU.
   Let's be smart.
2. **Collections of Visuals**: Along with the SceneCanvas, VisPy needs more
   Visuals that support defining multiple instances of the same object. VisPy
   has a very low-level "collections" set of objects, but these aren't
   accessible or usable to the higher-level Visuals/SceneCanvas interfaces. A
   solution to this may be a rewrite to some Visuals to allow for multiple
   instances or for a complete rewrite of parts of VisPy to detect when
   multiple of the same object are being created and combine them together for
   optimized drawing.
3. **Alternative Data Containers**: See 'Dask and CuPy Integration' below.
4. **Jupyter Widgets** (`#134 <https://github.com/vispy/vispy/issues/1989>`_, `#1989 <https://github.com/vispy/vispy/issues/1989>`_):
   VisPy's Jupyter widget does not perform well. It can
   draw most things nowadays, but eventually lags behind any updates whether
   they be from timers or user input.

Plotting API
^^^^^^^^^^^^

The Plotting API in VisPy has been a dream in the back of the VisPy developers'
minds since the beginning of development. While the plotting interfaces exist,
they are not very flexible and at times don't perform very well. It can be
difficult with the plotting APIs to customize all the pieces that you want to
or update data after the initial creation. This sometimes requires accessing
hidden (`_` prefix) attributes and going multiple levels deep into complex
(compound) visuals just to change the size or style of something. This
deserves a real specification and plan for how users can get the most out of
these interfaces so that they stay simple but useful.

Dask and CuPy Integration
^^^^^^^^^^^^^^^^^^^^^^^^^

Dask and CuPy arrays present a very interesting opportunity for VisPy to
display larger data and at faster speeds than previously possible. However,
VisPy doesn't currently make this easier or even possible in some cases.
With Dask, VisPy should be able to re-compute or re-load data that the user
provides and throw it to the GPU when it is ready. With CuPy users should be
able to do all their computations on the GPU and then let VisPy visualize
that data **without** ever needing to copy it back to the CPU.

See `#1985 <https://github.com/vispy/vispy/issues/1985>`_ and
`#1986 <https://github.com/vispy/vispy/issues/1986>`_ for more information
and discussion on these topics.

Low-level leakage
^^^^^^^^^^^^^^^^^

VisPy depends heavily on OpenGL for all of its drawing functionality. While
this performs well, we've had to bring some of the low-level logic of OpenGL
into higher levels of VisPy to make things work. As VisPy continues to grow
we'd like to make sure that any pieces specific to OpenGL stay in the low
level parts of VisPy and are accessed through defined interfaces.

See the "OpenGL, Vulkan, and WebGPU" section below for why this is important.

Primitive Visuals
^^^^^^^^^^^^^^^^^

Along the same lines of preventing low-level APIs leaking into higher levels,
we'd like to define a set of "primitive" Visual objects. These primitives
would define a set of basic functionality and that interact the closest with
the low-level OpenGL layers of VisPy. Using these primitives, users should be
able to easily create their own, more complex, visualizations without ever
needing to know the complexities of the underlying layers.

See the `VisPy Wiki <https://github.com/vispy/vispy/wiki/Primitive-Visuals>`_
for our attempt at defining these types of primitives.

See the "OpenGL, Vulkan, and WebGPU" section below for why this is important.

Road to Version 2.0
-------------------

We'll cross this bridge when we come to it, but maybe we can start planning
sooner rather than later.

OpenGL, Vulkan, and WebGPU
^^^^^^^^^^^^^^^^^^^^^^^^^^

VisPy currently strives for compliance with OpenGL 2 and OpenGL ES. This was
a goal of early VisPy in order to have compatibility with mobile platforms
including web browsers. Over the years this has become a major burden for
VisPy. We've been able to add functionality for things like Geometry shaders
and allow for newer GLSL shaders, but the majority of VisPy is still limited
to the features of old OpenGL.

New graphics APIs like Vulkan and WebGPU are meant to provide users with more
control, flexibility, and reliability. They are also more supported by
industry (ex. gaming). If VisPy wants to keep up with modern technology and
still provide its high level interfaces, it needs to be able to adopt new
graphics APIs like these. The "low-level leakage" and "primitive visuals"
described above are the first steps towards getting VisPy's source code
ready for this type of flexibility.

One library that VisPy is looking to as a future "graphics backend" is
Datoviz (https://datoviz.org/) which depends on Vulkan. By implementing a
set of primitive visuals, we hope that VisPy can provide the same
visualizations but with a completely different graphics technology doing the
drawing.

See `#1988 <https://github.com/vispy/vispy/issues/1988>`_ to track any
discussion and related issues.

Deprecation of "gloo" and GLIR
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the beginning of VisPy development, the GLIR (OpenGL Intermediate
Representation) was created to allow for the possibility of "remote" rendering.
This would allow users to define what they wanted, but have a remote system do
all the actual GPU number crunching. This is great in theory, but in practice
becomes extremely difficult to maintain and preserve performance. This was
extremely obvious when working with the Jupyter widget. GLIR is also very
OpenGL specific. As discussed above, this can only work for so long.

The one major benefit
of GLIR is the ability to save the commands for a visualization and then
"replay" them. This is really cool, but is almost never used as it is only
possible in the javascript vispy.js library (or at least used to be).
Put bluntly, VisPy isn't getting any benefit from GLIR and it will therefore
likely be deprecated in coming VisPy versions.

Along with GLIR, the "gloo" interface will also need to be deprecated. VisPy
development will focus on higher level functionality and let other libraries
like Datoviz focus on the low level. The "gloo" interfaces are extremely useful
for having full control over an OpenGL 2/ES visualization, but as described
above OpenGL 2 is old. Updating "gloo", or an interface like it, to work with
newer versions of OpenGL would be too much work at this point. What we're
really looking for is the type of control newer graphics libraries like Vulkan
can provide.
