# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from .. import gloo
from ..gloo import gl
from .transforms import STTransform, NullTransform
from .mesh import MeshVisual
from .components import (TextureComponent, VertexTextureCoordinateComponent,
                         TextureCoordinateComponent)


class ImageVisual(MeshVisual):
    """
    Visual subclass displaying an image. 
    
    Parameters:
        data : (height, width, 4) ubyte array
        method : str
            Selects method of rendering image in case of non-linear transforms.
            Each method produces similar results, but may trade efficiency 
            and accuracy. If the transform is linear, this parameter is ignored
            and a single quad is drawn around the area of the image.
            'subdivide': Image is represented as a grid of triangles with
                texture coordinates linearly mapped.
            'impostor': Image is represented as a quad covering the entire
                view, with texture coordinates determined by the transform. This
                produces the best transformation results, but may be slow.
        grid: (rows, cols)
            If method='subdivide', this tuple determines the number of rows and
            columns in the image grid.
    """
    def __init__(self, data, method='subdivide', grid=(10,10)):
        super(ImageVisual, self).__init__()
        
        self._data = None
        
        # maps from quad coordinates to texture coordinates
        self._tex_transform = STTransform() 

        self._texture = None
        self.set_data(data)
        self.set_gl_options(glCullFace=('GL_FRONT_AND_BACK',))
        
        self.method = method
        self.grid = grid
        
    def set_data(self, image):
        self._data = image
        self._texture = None

    def _build_data(self):
        # Construct complete data array with position and optionally color
        if self.transform.Linear:
            method = 'subdivide'
            grid = (1, 1)
        else:
            method = self.method
            grid = self.grid
        
        # TODO: subdivision and impostor modes should be handled by new components?
        if method == 'subdivide':
            # quads cover area of image as closely as possible
            w = 1.0 / grid[1]
            h = 1.0 / grid[0]
            
            quad = np.array([[0,0,0], [w,0,0], [w,h,0], 
                             [0,0,0], [w,h,0], [0,h,0]], 
                            dtype=np.float32)
            quads = np.empty((grid[1], grid[0], 6, 3), dtype=np.float32)
            quads[:] = quad
            
            mgrid = np.mgrid[0.:grid[1], 0.:grid[0]].transpose(1,2,0)[:, :, np.newaxis, :]
            mgrid[...,0] *= w
            mgrid[...,1] *= h
            
            quads[...,:2] += mgrid
            tex_coords = quads.reshape(grid[1]*grid[0]*6,3)
            vertexes = tex_coords.copy()
            vertexes[...,0] *= self._data.shape[1]
            vertexes[...,1] *= self._data.shape[0]
            MeshVisual.set_data(self, pos=vertexes)
            
            tex_coord_comp = TextureCoordinateComponent(tex_coords)
            
            self._program['map_local_to_nd'] = self.transform.shader_map()
        
        elif method == 'impostor':
            # quad covers entire view; frag. shader will deal with image shape
            quad = np.array([[-1,-1,0], [1,-1,0], [1,1,0], 
                             [-1,-1,0], [1,1,0], [-1,1,0]],
                            dtype=np.float32)
            MeshVisual.set_data(self, pos=quad)
            
            self._tex_transform.scale = (1./self._data.shape[0], 1./self._data.shape[1])
            total_transform = self._tex_transform * self.transform.inverse()
            tex_coord_comp = VertexTextureCoordinateComponent(total_transform)
            
            self._program['map_local_to_nd'] = NullTransform().shader_map()
            
        else:
            raise NotImplementedError
            
        self._texture = gloo.Texture2D(self._data)
        self._texture.interpolation = gl.GL_NEAREST
        
        self.color_components = [TextureComponent(self._texture, tex_coord_comp)]

    
    def _activate_transform(self):
        # this is handled in _build_data instead.
        pass
    
    def paint(self):
        if self._data is None:
            return
        
        if self._texture is None:
            self._build_data()
        
        super(ImageVisual, self).paint()
