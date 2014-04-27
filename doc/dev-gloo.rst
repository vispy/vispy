==================
The gloo interface
==================

Gloo provides a very convenient and pythonic interface to OpenGL objects such
as textures, frame buffer objects (FBO), vertex buffer object (VBO) and
shaders. All classes inherit from GLObject and provide a common interface for
activating and deactivating the object. However, the API has been made such
that you don't have to explicitly activate or deactivate objects, all is
handled automatically::

    program = Program(vertex, fragment, count=4)
    program['color']    = [(1,0,0,1), (0,1,0,1), (0,0,1,1), (1,1,0,1)]
    program['position'] = [(-1, -1),  (-1, +1),  (+1, -1),  (+1, +1)]
    ...
    program.draw(gl.GL_TRIANGLE_STRIP)
    ...



Vertex Buffer
=============

A VertexBuffer represents vertex data that can be uploaded to GPU memory. They
can have a local (CPU) copy or not such that in the former case, the buffer is
read-write while in the latter case, the buffer is write-only.

* The (internal) shape of a vertex buffer is always one-dimensional.
* The (internal) dtype of a vertex buffer is always structured.

Elementary allowed dtype are: ``np.uint8``, ``np.int8``, ``np.uint16``,
``np.int16``, ``np.float32``

All GPU operations are deferred and executed just-in time (automatic).


Creation from existing data
---------------------------

Use given data as CPU storage::

  V = VertexBuffer(data=data, store=True, copy=False)

Use a copy of given data as CPU storage::

  V = VertexBuffer(data=data, store=True, copy=True)

Do not use CPU storage::

  V = VertexBuffer(data=data, store=False)


Creation from dtype and size
----------------------------

Create a CPU storage with given size::

  V = VertexBuffer(dtype=dtype, size=size, store=True)

Do not use CPU storage::

  V = VertexBuffer(dtype=dtype, size=size, store=False)



Setting data (set_data)
-----------------------

Any contiguous block of data can be set using the ``set_data`` method. This
method can also be used to resize the buffer. When setting data, it is possible
to specify whether to store a copy of given data hence freezing the state of
the data. It is important because the actual upload is deferred and data can be
changed before the actual upload occurs.

This example results in 2 pending operations but only the "2" value will be
uploaded (2 in data[:10] and 2 in data[10:])::

  V = VertexBuffer(...)
  data[...] = 1
  V.set_data(data[:10], copy=False)
  data[...] = 2
  V.set_data(data[10:], copy=False)

This example results in 2 pending operations and the "1" and "2" values will
actually be uploaded (1 in data[:10] and 2 in data[10:])::

  V = VertexBuffer(...)
  data[...] = 1
  V.set_data(data[:10], copy=True)
  data[...] = 2
  V.set_data(data[10:], copy=True)



Setting data (setitem)
----------------------

If buffer has CPU storage, any numpy operations is allowed since the operation
is performed on CPU data and modified part are registered for uploading::

  V = VertexBuffer(...)
  V[:10] = data # ok
  V[::2] = data # ok

If buffer has no CPU storage, only numpy operations that affect a contiguous
block of data are allowed. This restriction is necessary because we cannot
upload strided data::

  V = VertexBuffer(...)
  V[:10] = data # ok
  V[::2] = data # error


Getting data (getitem)
----------------------

Accessing data from a VertexBuffer (base) returns a VertexBuffer (view) that is
linked to the base buffer. Accessing data from a buffer view is not allowed::

  V = VertexBuffer(...)
  Z1 = V[:10] # ok
  V[...] = 1  # ok
  Z2 = Z1[:5] # error


Resizing the buffer
-------------------

Whenever a buffer is resized, all pending operations are cleared and any existing
view on the buffer becomes invalid.



Index Buffer
============

A IndexBuffer represents indices data that can be uploaded to GPU memory. They
can have a local (CPU) copy or not such that in the former case, the buffer is
read-write while in the latter case, the buffer is write-only.

* The shape of an index buffer is always one-dimensional.
* The dtype of an index buffer is one of: np.uint8, np.uint16, np.uint32
* All GPU operations are deferred and executed just-in time (automatic).
* All vertex buffer methods and properties apply.



Program
=======

A program is an object to which shaders can be attached and linked to create
the program. It gives access to attributes and uniform through the
getitem/setitem.


Implicit buffer
---------------

If a vertex count is given at creation, a unique associated vertex buffer is
created automatically::

  program = Program(vertex, fragment, count=4)
  program['a_color']    = [ (1,0,0,1), (0,1,0,1), (0,0,1,1), (1,1,0,1) ]
  program['a_position'] = [ (-1,-1),   (-1,+1),   (+1,-1),   (+1,+1)   ]


Direct upload
-------------

If one wants to directly upload data (without intermediary vertex buffer), one
has to explicitly set the direct upload flag at creation::

  program = Program(vertex, fragment, direct=True)
  program['a_color']    = [ (1,0,0,1), (0,1,0,1), (0,0,1,1), (1,1,0,1) ]
  program['a_position'] = [ (-1,-1),   (-1,+1),   (+1,-1),   (+1,+1)   ]


Explicit grouped binding
------------------------

It is also possible to create vertex buffer and bind it automatically to the
program, provided buffer field names and attributes match::

  program = Program(vertex, fragment)
  vertices = np.zeros(4, [('a_position', np.float32, 2),
                          ('a_color',    np.float32, 4)])
  program.bind(VertexBuffer(vertices)
  program['a_color'] = [ (1,0,0,1), (0,1,0,1), (0,0,1,1), (1,1,0,1) ]
  program['a_position'] = [ (-1,-1),   (-1,+1),   (+1,-1),   (+1,+1)   ]


Explicit binding
----------------

Finally, for finer grain control, one can explicitly set each attribute or
uniform individually::

  program = Program(vertex, fragment)
  position = VertexBuffer(np.zeros((4,2), np.float32))
  position[:] = [((-1,-1),), ((-1,+1),), ((+1,-1),), ((+1,+1),)]
  program['a_position'] = position
  color = VertexBuffer(np.zeros((4,4), np.float32))
  color[:] = [((1,0,0,1),), ((0,1,0,1),), ((0,0,1,1),), ((1,1,0,1),)]
  program['a_color'] = color



Texture
=======

Textures represent texture data that can be uploaded to GPU memory. They
can have a local (CPU) copy or not such that in the former case, the texture is
read-write while in the latter case, the texture is write-only.

The (internal) shape of a texture is the size of the class +1:

  * Texture1D -> shape is two-dimensional (width, 1/2/3/4)
  * Texture2D -> shape is three-dimensional (height, width, 1/2/3/4)

The (internal) dtype of a texture is one of:

* ``np.int8``
* ``np.uint8``
* ``np.int16``
* ``np.uint16``
* ``np.int32``
* ``np.uint32``
* ``np.float32``


Creation from existing data
---------------------------

When creating a texture, the GPU format (RGB, RGBA,etc) of the texture is
deduced from the data dtype and shape.

  1. gl.GL_LUMINANCE
  2. gl.GL_LUMINANCE_ALPHA
  3. gl.GL_RGB
  4. gl.GL_RGBA


Use given data as CPU storage::

  T = Texture2D(data=data, store=True, copy=False)

Use a copy of given data as CPU storage::

  V = Texture2D(data=data, store=True, copy=True)

Do not use CPU storage::

  V = Texture2D(data=data, store=False)


Creation from dtype and size
----------------------------

When creating a texture, the GPU format (RGB, RGBA,etc) of the texture is
deduced from the dtype and the shape:

Create a CPU storage with given size::

  V = Texture2D(dtype=dtype, shape=shape, store=True)

Do not use CPU storage::

  V = Texture2D(dtype=dtype, shape=shape, store=False)


Setting data (setitem)
----------------------

If texture has CPU storage, any numpy operations is allowed since the operation
is performed on CPU data and modified part are registered for uploading::

  V = Texture2D(...)
  V[:10] = data # ok
  V[::2] = data # ok

If texture has no CPU storage, only numpy operations that affect a contiguous
block of data are allowed. This restriction is necessary because we cannot
upload strided data::

  V = Texture2D(...)
  V[:10] = data # ok
  V[::2] = data # error


Getting data (getitem)
----------------------

Accessing data from a Texture (base) returns a Texture (view) that is linked to
the base texture. Accessing data from a texture view is not allowed::

  V = Texture2D(...)
  Z1 = V[:10] # ok
  V[...] = 1  # ok
  Z2 = Z1[:5] # error


Resizing the texture
--------------------

Whenever a texture is resized, all pending operations are cleared and any
existing view on the texture becomes invalid.
