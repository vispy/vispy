# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import unittest

import numpy as np

from vispy.gloo import gl
from vispy import gloo


def _dummy(*args, **kwargs):
    """ Dummy method to replace all GL calls with.
    Return 1 for glGenTextures etc.
    """
    return 1


def _dummy_glGetProgramiv(handle, mode):
    if mode in (gl.GL_ACTIVE_ATTRIBUTES, gl.GL_ACTIVE_UNIFORMS):
        return 0
    else:
        return 1


def _dummy_glGetAttachedShaders(*args, **kwargs):
    return ()


class GLObjectTest(unittest.TestCase):

    def setUp(self):
        #print('Dummyfying gl namespace.')
        for key in dir(gl):
            if key.startswith('gl'):
                setattr(gl, key, _dummy)
        #
        for key in dir(gl.ext):
            if key.startswith('gl'):
                setattr(gl.ext, key, _dummy)
        #
        gl.glGetProgramiv = _dummy_glGetProgramiv
        gl.glGetAttachedShaders = _dummy_glGetAttachedShaders

    def tearDown(self):
        gl.use('desktop')

    def _fix_ob(self, ob):
        """ Modify object so we can keep track of its calls to _create,
        _update, etc.
        """
        ob._actions = []

        def _create():
            ob._actions.append('create')
            return ob.__class__._create(ob)

        def _activate():
            ob._actions.append('activate')
            return ob.__class__._activate(ob)

        def _deactivate():
            ob._actions.append('deactivate')
            return ob.__class__._deactivate(ob)

        def _update():
            ob._actions.append('update')
            return ob.__class__._update(ob)

        def _delete():
            ob._actions.append('delete')
            return ob.__class__._delete(ob)

        ob._create = _create
        ob._activate = _activate
        ob._deactivate = _deactivate
        ob._update = _update
        ob._delete = _delete

    def test_init(self):
        obj = gloo.GLObject()
        assert obj._handle == 0
        assert obj._need_update is False
        assert obj._valid is False
        # assert obj._id   == 1

    def test_buffer(self):

        # Some data that we need
        data = np.zeros(100, np.uint16)
        im2 = np.zeros((50, 50), np.uint16)
        im3 = np.zeros((20, 20, 20), np.uint16)
        shaders = gloo.VertexShader("x"), gloo.FragmentShader("x")

        items = [
            # Buffers
            (gloo.buffer.Buffer(target=gl.GL_ARRAY_BUFFER), 'set_data', data),
            (gloo.buffer.VertexBuffer(np.uint16), 'set_data', data),
            (gloo.buffer.ElementBuffer(np.uint16), 'set_data', data),
            # Textures
            (gloo.Texture2D(), 'set_data', im2),
            (gloo.Texture3D(), 'set_data', im3),
            # FBO stuff
            (gloo.RenderBuffer(), 'set_shape', (1, 1)),
            (gloo.FrameBuffer(), 'attach_color', gloo.RenderBuffer((1, 1))),
            # Shader stuff
            (gloo.VertexShader(), 'set_code', "x"),
            (gloo.FragmentShader(), 'set_code', "x"),
            (gloo.Program(), 'attach', shaders),
        ]

        for ob, funcname, value in items:
            self._fix_ob(ob)
            #print('Testing GLObject compliance for %s'
            #      % ob.__class__.__name__)

            # Initially a clear state
            self.assertEqual(ob._need_update, False)

            # Set value, now we should have a "dirty" state
            x = ob
            for part in funcname.split('.'):
                x = getattr(x, part)
            x(value)
            self.assertEqual(ob._need_update, True)

            # Activate the object
            ob.activate()
            # Now we should be activated
            self.assertEqual(len(ob._actions), 3)
            self.assertEqual(ob._actions[0], 'create')
            self.assertEqual(ob._actions.count('update'), 1)
            self.assertEqual(ob._actions.count('activate'), 1)

            # Deactivate
            ob.deactivate()
            # Now we should be deactivated
            self.assertEqual(len(ob._actions), 4)
            self.assertEqual(ob._actions[-1], 'deactivate')

            # Activate some more
            for i in range(10):
                ob.activate()

            # Create and update should not have been called
            self.assertEqual(ob._actions.count('create'), 1)
            self.assertEqual(ob._actions.count('update'), 1)

    def test_buffer_view(self):
        """ Same as above, but special case for VertexBufferView that
        needs special attention.
        """

        # Some "data"
        data = np.zeros(100, np.uint16)
        baseBuffer = gloo.buffer.VertexBuffer(np.uint16)

        # Create object
        ob = gloo.buffer.VertexBufferView(np.dtype(np.uint16), baseBuffer, 0)
        funcname = 'base.set_data'
        value = data

        self._fix_ob(ob)
        self._fix_ob(baseBuffer)

        # Initially a clear state
        self.assertEqual(ob._need_update, False)

        # Set value, now we should have a "dirty" state
        x = ob
        for part in funcname.split('.'):
            x = getattr(x, part)
        x(value)
        self.assertEqual(ob.base._need_update, True)

        # Activate the object
        ob.activate()
        # Now we should be activated
        self.assertEqual(len(ob._actions), 2)
        self.assertEqual(ob._actions[0], 'create')
        self.assertEqual(ob._actions.count('activate'), 1)
        # Now we should be activated
        self.assertEqual(len(ob.base._actions), 3)
        self.assertEqual(ob.base._actions[0], 'create')
        self.assertEqual(ob.base._actions.count('update'), 1)
        self.assertEqual(ob.base._actions.count('activate'), 1)

        # Deactivate
        ob.deactivate()
        # Now we should be deactivated
        self.assertEqual(len(ob.base._actions), 4)
        self.assertEqual(ob.base._actions[-1], 'deactivate')

        # Activate some more
        for i in range(10):
            ob.activate()

        # Create and update should not have been called
        self.assertEqual(ob._actions.count('create'), 1)
        self.assertEqual(ob._actions.count('update'), 0)

        # Create and update should not have been called
        self.assertEqual(ob.base._actions.count('create'), 1)
        self.assertEqual(ob.base._actions.count('update'), 1)

    def test_foo(self):
        pass
