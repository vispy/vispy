# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


from __future__ import division

import numpy as np

from ..base import System, ViewBox
from ...gloo import gl
from ...util import logger


class DrawingSystem(System):

    """ Simple implementation of a drawing engine.
    """

    def _process_init(self, viewbox, root):
        # Camera transform and projection are the same for the
        # entire scene
        self._camtransform = viewbox.camera.get_camera_transform()
        self._projection = viewbox.camera.get_projection(viewbox)
        # Prepare the viewbox (e.g. set up glViewport)
        self._prepare_viewbox(viewbox)
        # Store viewbox and root
        self._viewbox, self._root = viewbox, root
        # Return unit transform
        return np.eye(4)

    def _process_entity(self, entity, transform):
        logger.debug('processing entity %s' % entity)
        # Set transformation
        if entity.transform is not None:
            transform = np.dot(transform, entity.transform)
        # Store all components of the transform
        shaderTransforms = {}
        shaderTransforms['transform_model'] = transform
        shaderTransforms['transform_view'] = self._camtransform
        shaderTransforms['transform_projection'] = self._projection
        # Draw
        visual = entity.get_visual(self._root)
        if visual is not None:
            if visual.program is not None:
                visual.program.set_vars(shaderTransforms)
            visual.draw()
        # If a viewbox, render the subscene.
        if isinstance(entity, ViewBox):
            entity.process(self._root, 'draw')
        # Return new transform
        return transform

    def _prepare_viewbox(self, viewbox):
        logger.debug('preparing viewbox %s' % viewbox)
        M = viewbox.transform
        w, h = int(M[0, 0]), int(M[1, 1])
        x, y = int(M[-1, 0]), int(M[-1, 1])

        need_FBO = False
        need_FBO |= bool(
            M[
                0, 1] or M[
                0, 2] or M[
                1, 0] or M[
                1, 2] or M[
                2, 0] or M[
                2, 1])
        need_FBO |= (w, h) != viewbox.resolution

        # todo: take parent viewboxes into account.

        if need_FBO:
            # todo: we cannot use a viewbox or scissors, but need an FBO
            raise NotImplementedError('Need FBO to draw this viewbox')
        else:
            # nice rectangle, we can use viewbox and scissors
            gl.glViewport(x, y, w, h)
            gl.glScissor(x, y, w, h)
            gl.glEnable(gl.GL_SCISSOR_TEST)
            # Draw bgcolor
            gl.glClearColor(*viewbox.bgcolor)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
