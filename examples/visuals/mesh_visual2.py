# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" A Mesh Visual that uses the new shader Function.
"""

from __future__ import division

import numpy as np

#from .visual import Visual
#from ..shader.function import Function, Variable
#from ...import gloo

from vispy.scene.visuals.visual import Visual
from vispy.scene.shaders import ModularProgram, Function, Variable, Varying
from vispy import gloo


## Snippet templates (defined as string to force user to create fresh Function)
# Consider these stored in a central location in vispy ...


vertex_template = """
void main() {
}
"""

fragment_template = """
void main() {
}
"""

phong_template = """
vec4 phong_shading(vec4 color) {
    vec3 norm = normalize($normal.xyz);
    vec3 light = normalize($light_dir.xyz);
    float p = dot(light, norm);
    p = (p < 0. ? 0. : p);
    vec4 diffuse = $light_color * p;
    diffuse.a = 1.0;
    p = dot(reflect(light, norm), vec3(0,0,1));
    if (p < 0.0) {
        p = 0.0;
    }
    vec4 specular = $light_color * 5.0 * pow(p, 100.);
    return color * ($ambient + diffuse) + specular;
}
"""

## Functions that can be uses as is (don't have template variables)
# Consider these stored in a central location in vispy ...

color3to4 = Function("""
vec4 color3to4(vec3 rgb) {
    return vec4(rgb, 1.0);
}
""")

stub4 = Function("vec4 stub4(vec4 value) { return value; }")
stub3 = Function("vec4 stub3(vec3 value) { return value; }")


## Actual code


class Mesh(Visual):
    
    def __init__(self, parent, 
                 vertices, faces=None, normals=None, values=None):
        Visual.__init__(self, parent)
        
        # Create a program
        self._program = ModularProgram(vertex_template, fragment_template)
        
        # Define how we are going to specify position and color
        self._program.vert['gl_Position'] = 'vec4($position, 1.0)'
        self._program.frag['gl_FragColor'] = '$light($color)'
        
        # Define variables related to color. Only one is in use at all times
        self._variables = {}
        self._variables['u_color3'] = Variable('uniform vec3 u_color')
        self._variables['u_color4'] = Variable('uniform vec4 u_color')
        self._variables['a_color3'] = Variable('attribute vec3 a_color')
        self._variables['a_color4'] = Variable('attribute vec4 a_color')
        
        # Set color to a varying
        self._program.frag['color'] = Varying('v_color')
        
        # Init
        self.shading = 'plain'
        #
        self.set_vertices(vertices)
        self.set_faces(faces)
        self.set_normals(normals)
        self.set_values(values)
    
    def set_vertices(self, vertices):
        vertices = gloo.VertexBuffer(vertices)
        self._program.vert['position'] = vertices
    
    def set_faces(self, faces):
        if faces is not None:
            self._faces = gloo.IndexBuffer(faces)
        else:
            self._faces = None
    
    def set_normals(self, normals):
        self._normals = normals
        self.shading = self.shading  # Update
    
    def set_values(self, values):
        
        # todo: reuse vertex buffer is possible (use set_data)
        # todo: we may want to clear any color vertex buffers
        
        if isinstance(values, tuple):
            # Single value (via a uniform)
            values = [float(v) for v in values]
            if len(values) == 3:
                variable = self._variables['u_color3']
                variable.value = values
                self._program.frag['color'] = color3to4(variable)
            elif len(values) == 4:
                variable = self._variables['u_color4']
                variable.value = values
                self._program.frag['color'] = variable
            else:
                raise ValueError('Color tuple must have 3 or 4 values.')
        
        elif isinstance(values, np.ndarray):
            # A value per vertex, via a VBO
            
            if values.shape[1] == 1:
                # Look color up in a colormap
                raise NotImplementedError()
            
            elif values.shape[1] == 2:
                # Look color up in a texture
                raise NotImplementedError()
            
            elif values.shape[1] == 3:
                # Explicitly set color per vertex
                varying = Varying('v_color')
                self._program.frag['color'] = color3to4(varying)
                variable = self._variables['a_color3']
                variable.value = gloo.VertexBuffer(values)
                self._program.vert[varying] = variable
            
            elif values.shape[1] == 4:
                # Explicitly set color per vertex
                # Fragment shader
                varying = Varying('v_color')
                self._program.frag['color'] = varying
                variable = self._variables['a_color4']
                variable.value = gloo.VertexBuffer(values)
                self._program.vert[varying] = variable
            
            else:
                raise ValueError('Mesh values must be NxM, with M 1,2,3 or 4.')
        else:
            raise ValueError('Mesh values must be NxM array or color tuple')
    
    @property
    def shading(self):
        """ The shading method used.
        """
        return self._shading
    
    @shading.setter
    def shading(self, value):
        assert value in ('plain', 'flat', 'phong')
        self._shading = value
        # todo: add gouroud shading
        # todo: allow flat shading even if vertices+faces is specified.
        if value == 'plain':
            self._program.frag['light'] = stub4
        
        elif value == 'flat':
            pass
            
        elif value == 'phong':
            assert self._normals is not None
            # Apply phonmg function, 
            phong = Function(phong_template)
            self._program.frag['light'] = phong
            # Normal data comes via vertex shader
            phong['normal'] = Varying('v_normal')
            var = gloo.VertexBuffer(self._normals)
            self._program.vert[phong['normal']] = var
            # Additional phong proprties
            phong['light_dir'] = 'vec3(1.0, 1.0, 1.0)'
            phong['light_color'] = 'vec4(1.0, 1.0, 1.0, 1.0)'
            phong['ambient'] = 'vec4(0.3, 0.3, 0.3, 1.0)'
            # todo: light properties should be queried from the SubScene
            # instance.
    
    def draw(self, event):
        # Draw
        self._program.draw('triangles', self._faces)


## The code to show it ...

if __name__ == '__main__':
    
    from vispy import app
    from vispy.util.meshdata import sphere
    
    mdata = sphere(20, 20)
    faces = mdata.faces()
    verts = mdata.vertices() / 4.0
    verts_flat = mdata.vertices(indexed='faces').reshape(-1, 3) / 4.0
    normals = mdata.vertex_normals()
    normals_flat = mdata.vertices(indexed='faces').reshape(-1, 3) / 4.0
    colors = np.random.uniform(0.2, 0.8, (verts.shape[0], 3)).astype('float32')
    colors_flat = np.random.uniform(0.2, 0.8, 
                                    (verts_flat.shape[0], 3)).astype('float32')
    
    class Canvas(app.Canvas):
        def __init__(self):
            app.Canvas.__init__(self, close_keys='escape')
            self.size = 700,    700
            self.meshes = []
            
            # A plain mesh with uniform color
            offset = np.array([-0.7, 0.7, 0.0], 'float32')
            mesh = Mesh(None, verts+offset, faces, None,
                        values=(1.0, 0.4, 0.0, 1.0))
            self.meshes.append(mesh)
            
            # A colored mesh with one color per phase
            offset = np.array([0.0, 0.7, 0.0], 'float32')
            mesh = Mesh(None, verts_flat+offset, None, None,
                        values=colors_flat)
            self.meshes.append(mesh)
            
            # Same mesh but using faces, so we get interpolation of color
            offset = np.array([0.7, 0.7, 0.0], 'float32')
            mesh = Mesh(None, verts+offset, faces, None, values=colors)
            self.meshes.append(mesh)
            
            # Flat phong shading
            offset = np.array([0.0, 0.0, 0.0], 'float32')
            mesh = Mesh(None, verts_flat+offset, None, normals_flat, 
                        values=colors_flat)
            mesh.shading = 'phong'
            self.meshes.append(mesh)
            
            # Full phong shading
            offset = np.array([0.7, 0.0, 0.0], 'float32')
            mesh = Mesh(None, verts+offset, faces, normals, values=colors)
            mesh.shading = 'phong'
            self.meshes.append(mesh)
        
        def on_draw(self, event):
            gloo.set_viewport(0, 0, *self.size)
            for mesh in self.meshes:
                mesh.draw(self)
    
    c = Canvas()
    c.show()
    app.run()
