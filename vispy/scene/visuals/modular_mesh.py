# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division
from .modular_visual import ModularVisual


class Mesh(ModularVisual):
    """
    Displays a 3D triangle mesh.
    """
    def __init__(self, gl_options='translucent', faces=None, index=None, 
                 pos=None, z=0.0, color=None, shading=None, **kwargs):
        self._meshdata = None
        
        super(Mesh, self).__init__(**kwargs)
        self.set_gl_options(depth_test=True, cull_face='front_and_back')
        self.update_gl_options(gl_options)
        
        # todo: how should this be handled? Subclasses will often define
        # different set_data signatures.
        Mesh.set_data(self, faces=faces, index=index, pos=pos, z=z, color=color)
        
        if shading is not None:
            self.set_shading(shading)

    def set_data(self, vertices=None, faces=None, vertex_colors=None, 
                 face_colors=None, meshdata=None):
        """
        """
        
        if meshdata is not None:
            self._meshdata = meshdata
        else:
            self._meshdata = MeshData(vertices=vertices, faces=faces, 
                                      vertex_colors=vertex_colors,
                                      face_colors=face_colors)
        self.mesh_data_changed()
        
    def mesh_data_changed(self):
        
        
        
        
        # select input component based on pos.shape
        if pos is not None:
            if index is not None:
                index = index.astype(np.uint32)
            if pos.shape[-1] == 2:
                comp = XYPosComponent(xy=pos.astype(np.float32), 
                                      z=z, index=index)
                self.pos_components = [comp]
            elif pos.shape[-1] == 3:
                comp = XYZPosComponent(pos=pos.astype(np.float32), index=index)
                self.pos_components = [comp]
            else:
                raise Exception("Can't handle position data: %s" % pos)

        if color is not None:
            components = self.color_components
            if len(components) == 0:
                components = [None]
                
            if isinstance(color, tuple):
                components[0] = [UniformColorComponent(color)]
            elif isinstance(color, np.ndarray):
                if color.ndim == 1:
                    components[0] = [UniformColorComponent(color)]
                elif color.ndim > 1:
                    components[0] = [VertexColorComponent(color)]
            else:
                raise Exception("Can't handle color data: %r" % color)
            
            self.color_components = components
            
        self.update()

    def set_shading(self, mode):
        """ Configure the appearance of the mesh. 
        
        Parameters
        ----------
        mode : str
            Options are 'plain', 'flat', or 'smooth'.
        
        This method works by selecting a default set of color (fragment shader) 
        components. For finer control, use set_color_components.
        """
        components = self.color_components[:1]
        if mode == 'plain':
            pass
            
        elif mode == 'flat':
            normal_comp = VertexNormalComponent(mdata)
            components.append(ShadingComponent(normal_comp,
                                               lights=[((-1, 1, -1),
                                                        (1.0, 1.0, 1.0))],
                                               ambient=0.2))
            
        elif mode == 'smooth':
            #mesh = visuals.Mesh(pos=mdata.vertices(indexed='faces'))
            normal_comp = VertexNormalComponent(mdata, smooth=False)
            components.append(ShadingComponent(normal_comp,
                                               lights=[((-1, 1, -1),
                                                        (1.0, 1.0, 1.0))],
                                               ambient=0.2))
        
        else:
            raise ValueError('mode argument must be "plain", "flat", or '
                             '"smooth".')
            
        self.color_components = components
        