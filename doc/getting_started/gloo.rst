Getting Started - gloo
======================

The gloo layer of VisPy is the lowest level interface and is the closest thing
to OpenGL that VisPy provides. This also means it is the most complicated.
While OpenGL is complicated, gloo tries to provide a simple to use
object-oriented layer on top of that. The guide below will walk through the
basics of using VisPy's gloo interface to create a visualization.

.. include:: _canvas_app.rst

Basic Script
------------

To start any gloo visualization we will need to create a ``Canvas`` object and
an ``Application``. Here is the most basic working example we can create:

.. code-block:: python

    import sys
    from vispy import app, gloo

    canvas = app.Canvas(keys='interactive')


    @canvas.connect
    def on_draw(event):
        gloo.set_clear_color((0.2, 0.4, 0.6, 1.0))
        gloo.clear()


    canvas.show()

    if __name__ == '__main__' and sys.flags.interactive == 0:
        app.run()

If you run the above code you should see a single window with a solid
blue-ish background.

Let's go through this code one chunk at a time:

1. We start out by importing the the `sys` module from the Python standard
   library followed by the vispy :mod:`~vispy.app` and :mod:`~vispy.gloo`
   modules.
2. We create a ``Canvas`` object representing the overall space
   where our visualization will take place.
3. We define a simple "on_draw" function telling OpenGL to fill the
   Canvas with a specific RGBA (Red, Green, Blue, Alpha) color. The color
   components are defined as floating point numbers between 0 and 1.
   We use the ``canvas.connect`` decorator method to attach this method
   to any "draw" events coming from the canvas. When using this technique
   the function must be named ``on_<event>``. For more on the available
   events that can be connected to, see the
   :class:`vispy.app.canvas.Canvas` docstring.
4. We call :meth:`canvas.show() <vispy.app.canvas.Canvas.show>` to display
   the Canvas object on the screen. VisPy will talk to the underlying GUI
   backend (PyQt, Wx, etc) to construct a native GUI "widget" with our
   OpenGL visualization inside.
5. The script ends with us running a default VisPy
   :class:`~vispy.app.application.Application` object. Later on we'll see
   how we can define the exact Application we want to use, but in this early
   stage we won't need to. The if statement here is a common occurrence in
   VisPy example scripts so that the Application is only started when the
   code is run as a script (instead of imported). This also helps with more
   advanced usage where we run this script in an interactive Python
   interpreter.

.. note::

    The above code is also available in the
    :ref:`examples/gloo/start.py <sphx_glr_gallery_gloo_start.py>` script.

Basic Script (Alternative)
--------------------------

Another common way to structure a script like this is to subclass the
``Canvas`` class and override the necessary methods directly. This can be
useful if you want to keep all parts of your visualization contained in the
``Canvas`` object instead of throughout a script. Here is what the above
"connect style" script would look like as a subclass:

.. code-block:: python

    import sys
    from vispy import app, gloo

    class MyCanvas(app.Canvas):
        def on_draw(self, event):
            gloo.set_clear_color((0.2, 0.4, 0.6, 1.0))
            gloo.clear()


    canvas = MyCanvas(keys='interactive')
    canvas.show()

    if __name__ == '__main__' and sys.flags.interactive == 0:
        app.run()

Create an OpenGL Program
------------------------

As mentioned earlier, the ``gloo`` interface provides a low-level
object-oriented interface on top of OpenGL. If we want to do anything more
complicated that a solid color, we'll need to start using these OpenGL
objects. We'll start with the below code to draw a simple shape in our
Canvas. As mentioned in :doc:`index`, if you aren't familiar with OpenGL then
it is highly recommended that you read :doc:`modern-gl` before diving into
the below code.

.. code-block:: python

    from vispy import app, gloo
    from vispy.gloo import Program

    vertex = """
        attribute vec4 color;
        attribute vec2 position;
        varying vec4 v_color;
        void main()
        {
            gl_Position = vec4(position, 0.0, 1.0);
            v_color = color;
        } """

    fragment = """
        varying vec4 v_color;
        void main()
        {
            gl_FragColor = v_color;
        } """


    class Canvas(app.Canvas):
        def __init__(self):
            super().__init__(size=(512, 512), title='Colored quad',
                             keys='interactive')

            # Build program
            self.program = Program(vertex, fragment, count=4)

            # Set uniforms and attributes
            self.program['color'] = [(1, 0, 0, 1), (0, 1, 0, 1),
                                     (0, 0, 1, 1), (1, 1, 0, 1)]
            self.program['position'] = [(-1, -1), (-1, +1),
                                        (+1, -1), (+1, +1)]

            gloo.set_viewport(0, 0, *self.physical_size)

            self.show()

        def on_draw(self, event):
            gloo.clear()
            self.program.draw('triangle_strip')

        def on_resize(self, event):
            gloo.set_viewport(0, 0, *event.physical_size)

    if __name__ == '__main__':
        c = Canvas()
        app.run()

Similar to the previous example, we've created a subclass of the ``Canvas``
object to hold on to all of the objects we create. We start by defining an
OpenGL :class:`~vispy.gloo.program.Program` which expects two shaders in the
simplest case: a vertex shader and a fragment shader.

Now that we have the Program, we are able to start setting uniforms and
attributes used by the shaders. In this example we've included the
``.show()`` call inside the ``__init__`` method so the Canvas is shown as soon
as it is created.

Lastly, we create two event handlers. One for the "resize" event so when the
user resizes the GUI window we can update the size of the OpenGL canvas
(viewport). The other handler is for "draw" where we clear the canvas,
setting it to the "clear color" of white, and then tell our GL Program to draw
or execute itself.

When we run this example we should see something like this:

.. image:: ../gallery/gloo/images/sphx_glr_colored_quad_001.png
    :alt: Screenshot of examples/gloo/colored_quad.py example script.
    :class: sphx-glr-single-img

This shape was created by drawing a ``"triangle_strip"`` using the coordinates
we assigned to the `position` attribute. Colors are interpolated between the
4 colors we assigned to each vertex (``color``) automatically by the GPU.
Under the hood, VisPy automatically
converts these positions and colors to numpy arrays. For the positions it
creates a
:class:`~vispy.gloo.buffer.VertexBuffer` object to store them. We could have
done this ourselves by replacing this line with:

.. code-block:: python

    self._program['position'] = gloo.VertexBuffer(pos_np_arr)

With this basic template, you can now start modifying the shader code,
or provide different uniforms and attributes. With the right setup, you can
also change the drawing method used (ex. 'points' or 'lines' instead of
'triangle_strip').

.. note::

    The above code is also available in the
    :ref:`examples/gloo/colored_quad.py <sphx_glr_gallery_gloo_colored_quad.py>` script.

Timers
------

A common requirement of any visualization is to make changes over time. VisPy
provides a generic :class:`~vispy.app.timer.Timer` class to help with this.
Let's take the quad example above and make a few modifications. First, we'll
create a :class:`~vispy.app.timer.Timer` in the ``Canvas.__init__`` method.
We'll also define a ``clock`` instance variable to use in our shader later
and then we'll start the timer.

.. code-block:: python

    self.program['theta'] = 0.0
    self.timer = app.Timer('auto', self.on_timer)
    self.clock = 0
    self.timer.start()

We first set a new uniform in our shader called ``theta`` which we'll
use later on. The ``'auto'`` setting tells the timer to fire as quickly as
quickly as it can (in between drawing and other GUI events). We've connected
this timer to a new ``on_timer`` method which will be executed whenever the
timer is triggered.

.. code-block:: python

    def on_timer(self, event):
        self.clock += 0.001 * 1000.0 / 60.
        self.program['theta'] = self.clock
        self.update()

In this method, we're updating our special ``clock`` counter variable,
updating that ``theta`` uniform in our shader, and finally we call
``self.update()`` which tells the ``Canvas`` to start redrawing itself.

.. note::

    The method name ``on_timer`` is by convention, but can be named anything.

Lastly, we update our vertex shader so the coordinates we provide to the
OpenGL program are adjusted based on our new ``theta`` uniform.

.. code-block:: python

    vertex = """
        uniform float theta;
        attribute vec4 color;
        attribute vec2 position;
        varying vec4 v_color;
        void main()
        {
            float ct = cos(theta);
            float st = sin(theta);
            float x = 0.75* (position.x*ct - position.y*st);
            float y = 0.75* (position.x*st + position.y*ct);
            gl_Position = vec4(x, y, 0.0, 1.0);
            v_color = color;
        } """

Putting it all together our new script looks like this:

.. code-block:: python

    from vispy import gloo, app
    from vispy.gloo import Program

    vertex = """
        uniform float theta;
        attribute vec4 color;
        attribute vec2 position;
        varying vec4 v_color;
        void main()
        {
            float ct = cos(theta);
            float st = sin(theta);
            float x = 0.75* (position.x*ct - position.y*st);
            float y = 0.75* (position.x*st + position.y*ct);
            gl_Position = vec4(x, y, 0.0, 1.0);
            v_color = color;
        } """

    fragment = """
        varying vec4 v_color;
        void main()
        {
            gl_FragColor = v_color;
        } """


    class Canvas(app.Canvas):
        def __init__(self):
            super().__init__(size=(512, 512), title='Rotating quad',
                             keys='interactive')
            # Build program & data
            self.program = Program(vertex, fragment, count=4)
            self.program['color'] = [(1, 0, 0, 1), (0, 1, 0, 1),
                                     (0, 0, 1, 1), (1, 1, 0, 1)]
            self.program['position'] = [(-1, -1), (-1, +1),
                                        (+1, -1), (+1, +1)]
            self.program['theta'] = 0.0

            gloo.set_viewport(0, 0, *self.physical_size)
            gloo.set_clear_color('white')

            self.timer = app.Timer('auto', self.on_timer)
            self.clock = 0
            self.timer.start()

            self.show()

        def on_draw(self, event):
            gloo.clear()
            self.program.draw('triangle_strip')

        def on_resize(self, event):
            gloo.set_viewport(0, 0, *event.physical_size)

        def on_timer(self, event):
            self.clock += 0.001 * 1000.0 / 60.
            self.program['theta'] = self.clock
            self.update()


    if __name__ == '__main__':
        c = Canvas()
        app.run()

The end result is a 2D square that rotates for every timer event.

.. image:: ../gallery/gloo/images/sphx_glr_rotating_quad_001.gif
    :alt: Screenshot of examples/gloo/colored_quad.py example script.
    :class: sphx-glr-single-img

.. note::

    The above code is also available in the
    :ref:`examples/gloo/rotating_quad.py <sphx_glr_gallery_gloo_rotating_quad.py>` script.

Keyboard Events
---------------

So far our examples haven't included any user interaction. The easiest way
to include some is to attach meaning to certain key presses. We can update
our example to include a "pause" button on the animation. We add one new
method to handle all keyboard events.

.. code-block:: python

    def on_key_press(self, event):
        if event.text == ' ':
            if self.timer.running:
                self.timer.stop()
            else:
                self.timer.start()

This method is automatically executed when the ``Canvas`` detects a key press.
The ``event.text`` is used to check for the Spacebar being pressed. If the
timer is running, we stop it, otherwise we start it.

Other Topics
------------

That's it for the "Getting Started" topics for the gloo interface. Now it is
time to get coding and exploring the other parts of the documentation. If you
think something is missing here and would make for a really good
"Getting Started" topic, please create an issue on GitHub. See
:doc:`../community` for more information.
