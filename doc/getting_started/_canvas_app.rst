Getting System Information
--------------------------

A good quick way of checking if VisPy is properly installed is to print out
system information. This output includes information like what backends you
have installed as well as information that can be gathered from OpenGL about
your GPU. This can be very important information to provide to VisPy
maintainers when filing bugs or asking questions. To get this information,
you can run the following python code:

.. code-block:: python

    import vispy
    print(vispy.sys_info())

.. note::

    This can be done in a one-liner from the command line with::

        python -c "import vispy; print(vispy.sys_info())"

The output of this should look something like the below, but will ultimately
depend on your environment and your machine.

::

    Platform: Linux-5.4.0-7642-generic-x86_64-with-debian-bullseye-sid
    Python:   3.7.6 | packaged by conda-forge | (default, Mar 23 2020, 23:03:20)  [GCC 7.3.0]
    NumPy:    1.18.1
    Backend:  PyQt5
    pyqt4:    None
    pyqt5:    ('PyQt5', '5.12.3', '5.12.5')
    pyside:   None
    pyside2:  None
    pyglet:   None
    glfw:     None
    sdl2:     None
    wx:       None
    egl:      EGL 1.5 NVIDIA: OpenGL_ES OpenGL
    osmesa:   None
    _test:    None

    GL version:  '4.6.0 NVIDIA 455.28'
    MAX_TEXTURE_SIZE: 32768
    Extensions: 'GL_AMD_multi_draw_indirect ...'

One important thing to look for is the "GL version". If you see an empty string
here or got an error when running this command, this likely means your system's
OpenGL library is not properly installed or can't be found by VisPy. You may
need to upgrade or re-install your GPU drivers to fix this or OpenGL may not
be compatible with your system.

The Canvas and The Application
------------------------------

There are two things that are common across all of the VisPy interfaces in one
way or another:

1. One ``Application`` instance
2. At least one ``Canvas`` (or subclass) instance

The Application
^^^^^^^^^^^^^^^

The VisPy ``Application`` object wraps the high-level event loop logic of
the VisPy backend you use (PyQt5, Wx, etc). In most cases you don't have
to know too much about this, but you do need to create and run the
application which we'll see below. If the application is not started, VisPy
will not be able to process events and won't run properly. Note that just like
with any GUI framework, calling the ``.run()`` method of the application is
a blocking call. Nothing after the ``.run()`` call will be executed until the
application is stopped, usually by closing your GUI window.

The Canvas
^^^^^^^^^^

The ``Canvas`` object will be your main way of using and controlling VisPy.
Depending on the VisPy interface you're using, you'll either be using the
``Canvas``, ``SceneCanvas``, or creating ``Figure`` objects. While these
different types of canvases are built on each other, they will almost never
be used in the same application. To help keep your code easy to understand
it is best not to mix these classes or their subcomponents.

