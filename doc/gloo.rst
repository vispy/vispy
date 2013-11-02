=====================================
The object oriented OpenGL API (gloo)
=====================================

.. automodule:: vispy.gloo


Base class
==========


.. autoclass:: vispy.gloo.GLObject
    :members:



Classes related to shaders
==========================

.. autoclass:: vispy.gloo.Program
    :members:


.. autoclass:: vispy.gloo.VertexShader
    :members:

.. autoclass:: vispy.gloo.FragmentShader
    :members:

.. autoclass:: vispy.gloo.shader.Shader
    :members:



Buffer classes
==============


.. autoclass:: vispy.gloo.VertexBuffer
    :members:

.. autoclass:: vispy.gloo.ElementBuffer
    :members:

.. autoclass:: vispy.gloo.buffer.DataBuffer
    :members:

.. autoclass:: vispy.gloo.buffer.Buffer
    :members:


Texture classes
===============

.. autoclass:: vispy.gloo.Texture2D

.. autoclass:: vispy.gloo.Texture3D

.. autoclass:: vispy.gloo.TextureCubeMap

.. autoclass:: vispy.gloo.texture.Texture
    :members:


Classes related to FBO
======================

.. autoclass:: vispy.gloo.FrameBuffer
    :members:

.. autoclass:: vispy.gloo.RenderBuffer
    :members:


vispy.gloo.gl - low level GL API
================================

Vispy also exposes a (low level) functional GL API. At this point gloo
is not yet fully independenat since it does not cover functions like
glClear().

 `vispy.gloo.gl docs <gl.html>`_
 