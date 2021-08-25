FAQ
===

VisPy is a big project with a lot of features and sometimes a couple ways to
do things. It sits on top of the very complex OpenGL library. We've tried to
document what we could in an organized and easy to find manner, but some
topics don't quite fit. This set of Frequently Asked Questions is where you'll
find the answer to some of these miscellaneous questions.

Why is my visualization slower when I add more Visual objects?
--------------------------------------------------------------

Each Visual object in VisPy is an OpenGL Program consisting of at least a
vertex shader and a fragment shader (see :doc:`getting_started/modern-gl`).
In general, except for some very specific cases, OpenGL Programs can only
be executed one at a time by a single OpenGL context. This means that in
your VisPy visualization each Visual object you tell VisPy to draw will
extend how long each update (draw) takes. When frames per second (FPS) or
responsiveness are a concern, this means each Visual you add reduces the
performance of your visualization.

While VisPy is constantly striving to improve performance, there are things
that you can do in the mean time (depending on your particular case). The
most important change that you can make is to lower the number of Visual
objects you have. For a lot of Visuals it is possible to combine them into
one by putting a little extra work into the data you provide them. For example,
instead of creating 10 separate LineVisuals, create 1 LineVisual that draws
10 lines. While this is a simple example, the same concept applies to other
types of Visuals in VisPy and more complex use cases. As a last resort for
the most complex cases, a custom Visual (custom shader code) may be necessary.
Before writing a custom Visual, check with VisPy maintainers by asking a
question on gitter or creating a question as a GitHub issue.

Is VisPy multi-threaded or thread-safe?
---------------------------------------

VisPy does not have any special multi-thread or multi-process handling except
for the funcionality provided by the GUI framework backends that it uses. For
example, PyQt5/PySide2 provide QThread objects for running code in another
thread. These libraries also provide ways of transferring data safely or
communicating between threads; mainly signals and slots. However, there is a
limit to what operations can be performed outside the main thread.

The main or GUI thread for most GUI frameworks is the **only** thread that can
perform drawing operations or operations that will trigger drawing. This
includes OpenGL functions. This means
that calling ``self.update()`` on a VisPy ``Canvas`` or ``Visual`` object must
ultimately be done in the main thread. Data that will be drawn can be created
or updated in a secondary thread, but the main/GUI thread must still be the
one to do the redraw. Since many Visual objects automatically call
``self.update()`` for property or data modifications this can be difficult to
do in the most performant way. Updates or requests for changes to better support
thread-safe data updates are welcome.

How to render headless/off-screen with VisPy?
---------------------------------------------

There are two strategies to render without windows with VisPy:

1. Use Xvfb that simulates an X server in memory without displaying windows.
   This can be used with any VisPy backend.
2. Use a backend that directly renders into memory buffers, e.g. OSMesa or EGL
   (`further info <https://stackoverflow.com/a/55758789>`_).

Then, in your VisPy script, use ::

    image = canvas.render()
    import imageio
    imageio.imwrite("rendered.png", image)

to save the rendered scene to an image file.

Xvfb
^^^^

Wrap the command to launch your script with ``xfvb-run``::

    xvfb-run -a python my_script.py

https://www.x.org/releases/X11R7.6/doc/man/man1/Xvfb.1.xhtml

OSMesa
^^^^^^

Using the OSMesa (Off-Screen Mesa) backend::

    import vispy
    vispy.use("osmesa")

VisPy tries to detect the OSMesa shared library, but, if needed, it can be set
explicitly with ::

    export OSMESA_LIBRARY=/usr/lib/libOSMesa.so

https://mesa-docs.readthedocs.io/en/latest/osmesa.html

EGL
^^^

Using the EGL backend::

    import vispy
    vispy.use("egl")

VisPy tries to detect the EGL shared library, but, if needed, it can be set
explicitly with ::

    # Choose one, or adapt to your system.
    export EGL_LIBRARY=/usr/lib/libEGL.so
    export EGL_LIBRARY=/usr/lib/libEGL_mesa.so
    export EGL_LIBRARY=/usr/lib/libEGL_nvidia.so

https://en.wikipedia.org/wiki/EGL_(API)

How to achieve transparency with 2D objects?
--------------------------------------------

With objects that lie in a 2D plane, e.g. images, it is possible to get a
translucent effect (i.e. partial transparency, a see-through effect) by
positioning them at different depth levels in the viewing direction and by
drawing the visuals from furthest to closest with the appropriate blending
mode.

Here are the key steps to achieve this with two
:class:`~vispy.scene.visuals.Image` visual nodes in a
:class:`~vispy.scene.canvas.SceneCanvas`:

1. Set the opacity value in the alpha channel of the images::
  
    # A white image with integer values between 0 and 255.
    image_data1 = np.ones((200, 300, 4), dtype='uint8')
    # Half translucent.
    image_data1[..., 3] = 128

    # A blue image with float values between 0 and 1.
    image_data2 = np.zeros((200, 300, 4), dtype='np.float32')
    image_data2[..., 2]  = 1.0  # Blue.
    # A bit more translucent.
    image_data2[..., 3] = 0.25

    visual1 = Image(image_data1)
    visual2 = Image(image_data2)

2. Position the visuals at different depth levels (z-levels) in the viewing
   direction::

    from vispy.visuals import transforms
    visual1.transform = transforms.STTransform(translate=(0, 0, 1))
    visual2.transform = transforms.STTransform(translate=(0, 0, 2))

   A higher ``z`` value means further back, assuming the viewing direction is
   the ``+z`` axis, e.g. the default for a
   :class:`~vispy.scene.cameras.PanZoomCamera`.

3. Draw the visuals from back to front by setting the draw
   :obj:`~vispy.scene.node.Node.order` of the nodes manually::

    visual2.order = 1  # Furthest, drawn first.
    visual1.order = 2  # Closest, drawn second.

This requires depth testing and blending enabled. An appropriate blending
function is, for example, ``(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)``
with `glBlendFunc <https://docs.gl/es2/glBlendFunc>`_ in OpenGL.
This is the default on the :class:`~vispy.scene.visuals.Image` visual node, but
otherwise it can be set with ::

    visual1.set_gl_state('translucent')

which is a shortcut for ::

    visual1.set_gl_state(depth_test=True, cull_face=False, blend=True,
                         blend_func=('src_alpha', 'one_minus_src_alpha'))

How do I cite VisPy?
--------------------

See the VisPy repository for citation information:
https://github.com/vispy/vispy/blob/main/CITATION.rst
