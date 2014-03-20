# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Notes:

  - Should have swappable input component to allow a variety of different 
    vertex inputs:
        2d attribute + z uniform
        3d attribute
        2d attribute + z uniform + index
        3d attribute + index
        1d attribute + x/y ranges (surface plot)
        (and any other custom input component the user might come up with)
        
  - Should have swappable / chainable fragment components:
        Per-vertex normals (for smooth surfaces)
        Per-face normals (for faceted surfaces)
        Colors per-vertex, per-face
        Materials - phong, etc.
        Textures - color, bump map, spec map, etc
        Wireframe rendering (note this might require vertex modification)
        
  - For efficiency, the vertex inputs should allow both pre-index and 
    unindexed arrays. However, many fragment shaders may require pre-indexed
    arrays. For example, drawing faceted surfaces is not possible with 
    unindexed arrays since the normal vector changes each time a vertex is
    visited.
        => this means that input components need a way to convert their data
           and suggest a different input component (?)
        => More generally, we need to be able to map out all of the available
           pathways and choose the most efficient one based on the input
           data format (to avoid unnecessary conversions) and the requirements
           of individual components (including indexed/unindexed, whether
           geometry shaders are available, ...)
    
  - Fragment shaders that do not need normals should obviously not compute them
  
  - Some materials require a normal vector, but there may be any number of
    ways to generate a normal: per-vertex interpolated, per-face, bump maps,
    etc. This means we need a way for one material to indicate that it requires
    normals, and a way to tell the component which normal-generating component
    it should use.
        => Likewise with colors. In fact, normals and colors are similar enough
           that they could probably share most of the same machinery..
           

    => Color chain   \
                      ===>  Material chain
    => Normal chain  /

    Examples:
        Color input / filters:
            uniform color
            color by vertex, color by face
            texture color
            float texture + colormap
            color by height
            grid contours
            wireframe
        
        Normal input:
            normal per vertex
            normal per face
            texture bump map
            texture normal map
        
        Material composition:
            shaded / facets
            shaded / smooth
            phong shading

"""


from __future__ import division

import numpy as np

from .. import gloo
from .visual import Visual, VisualComponent
from .transforms import NullTransform
from ..shaders.composite import ModularProgram, Function
from ..util.meshdata import MeshData


VERTEX_SHADER = """
// local_position function must return the current vertex position
// in the Visual's local coordinate system.
vec4 local_position();

// mapping function that transforms from the Visual's local coordinate
// system to normalized device coordinates.
vec4 map_local_to_nd(vec4);

// generic hook for executing code after the vertex position has been set
void vert_post_hook();

void main(void) {
    vec4 local_pos = local_position();
    vec4 nd_pos = map_local_to_nd(local_pos);
    gl_Position = nd_pos;
    
    vert_post_hook();
}
"""

FRAGMENT_SHADER = """
// Fragment shader consists of only a single hook that is usually defined 
// by a chain of functions, each which sets or modifies the current fragment
// color, or discards it.
vec4 frag_color();

void main(void) {
    gl_FragColor = frag_color();
}
"""



class MeshVisual(Visual):
    """
    Displays a 3D triangle mesh.
    """
    def __init__(self, **kwds):
        super(MeshVisual, self).__init__()
        
        self._program = ModularProgram(VERTEX_SHADER, FRAGMENT_SHADER)
        
        self.transform = NullTransform()
        
        # Generic chains for attaching post-processing functions
        self._program.add_chain('vert_post_hook')
        self._program.add_chain('frag_color')
        
        # Components for plugging different types of position and color input.
        self._pos_component = None
        self._color_component = None
        self.pos_component = XYZPosComponent()
        self._frag_components = []
        self.fragment_components = [UniformColorComponent()]
        
        glopts = kwds.pop('gl_options', 'opaque')
        self.set_gl_options(glopts)
        
        if kwds:
            self.set_data(**kwds)

    def set_data(self, pos=None, faces=None, z=0.0, color=(1,1,1,1)):
        """
        *pos* must be array of shape (..., 2) or (..., 3).
        *z* is only used in the former case.
        
        *faces* is not supported yet.
        """
        # select input component based on pos.shape
        if pos is not None:
            if pos.shape[-1] == 2:
                if not isinstance(self.pos_component, XYPosComponent):
                    self.pos_component = XYPosComponent()
                self.pos_component.set_data(xy=pos, z=z, faces=faces)
            elif pos.shape[-1] == 3:
                if not isinstance(self.pos_component, XYZPosComponent):
                    self.pos_component = XYZPosComponent()
                self.pos_component.set_data(pos=pos, faces=faces)
            
        if isinstance(color, tuple):
            self.fragment_components = [UniformColorComponent(color)]
        elif isinstance(color, np.ndarray):
            self.fragment_components = [VertexColorComponent(color)]
            

    def paint(self):
        super(MeshVisual, self).paint()
        
        modes = set(self.pos_component.supported_draw_modes)
        for comp in self._frag_components:
            modes &= set(comp.supported_draw_modes)
        
        if len(modes) == 0:
            raise Exception("Visual cannot paint--no mutually supported "
                            "draw modes between components.")
        
        #TODO: pick most efficient draw mode!
        mode = list(modes)[0]
            
        # activate all components
        self.pos_component.activate(self._program, mode)
        for comp in self._frag_components:
            comp.activate(self._program, mode)
        
        # TODO: this must be optimized.
        self._program['map_local_to_nd'] = self.transform.shader_map()
        
        self._program.draw(gloo.gl.GL_TRIANGLES, self.pos_component.index)

    @property
    def pos_component(self):
        return self._pos_component

    @pos_component.setter
    def pos_component(self, component):
        if self._pos_component is not None:
            self._pos_component._detach(self)
            self._pos_component = None
        component._attach(self)
        self._pos_component = component
        self.events.update()
        
    ## TODO: Allow multiple color components to be added in series
    #@property
    #def color_input_component(self):
        #return self._color_input_component

    #@color_input_component.setter
    #def color_input_component(self, component):
        #if self._color_input_component is not None:
            #self._color_input_component._detach(self)
            #self._color_input_component = None
        #component._attach(self)
        #self._color_input_component = component
        #self.events.update()

    @property
    def fragment_components(self):
        return self._frag_components[:]
    
    @fragment_components.setter
    def fragment_components(self, comps):
        for comp in self._frag_components:
            comp._detach()
        self._frag_components = comps
        for comp in self._frag_components:
            comp._attach(self)
        self.events.update()
        

class MeshComponent(VisualComponent):
    
    DRAW_PRE_INDEXED = 1
    DRAW_UNINDEXED = 2
    
    def __init__(self):
        super(MeshComponent, self).__init__()
        
    @property
    def supported_draw_modes(self):
        """
        A tuple of the draw modes (either DRAW_PRE_INDEXED, DRAW_UNINDEXED, or
        both) currently supported by this component.        
        """
        raise NotImplementedError

    def update(self):
        """
        Inform visual that this component has changed.
        """
        if self.visual is not None:
            self.visual.events.update()

    def activate(self, program):
        """
        Attach to *program* all functions and data required by this component.
        """
        raise NotImplementedError

    
class XYPosComponent(MeshComponent):
    """
    generate local coordinate from xy (vec2) attribute and z (float) uniform
    """
    CODE = """
        vec4 $input_xy_pos() {
            return vec4($xy_pos, $z_pos, 1.0);
        }
        """

    def __init__(self, xy=None, z=0.0, faces=None):
        super(XYPosComponent, self).__init__()
        self.shader_func = Function(self.CODE)
        self._xy = None
        self._z = 0.0
        self._faces = False
        self._vbo = None
        self._ibo = None
        self.set_data(xy, z, faces)
        
    @property
    def supported_draw_modes(self):
        # TODO: Add support for converting between pre-indexed and unindexed
        if self._faces is False:
            return (self.DRAW_PRE_INDEXED,)
        else:
            return (self.DRAW_UNINDEXED,)

    def set_data(self, xy=None, z=None, faces=None):
        if xy is not None:
            self._xy = xy
        if z is not None:
            self._z = z
        if faces is not None:
            self._faces = faces
        # TODO: might be better to re-upload data rather than creating
        # a new VB, if possible.
        self._vbo = None
        self.update()

    @property
    def vbo(self):
        if self._vbo is None:
            self._vbo = gloo.VertexBuffer(self._xy)
        return self._vbo

    @property
    def ibo(self):
        if self._ibo is None:
            self._ibo = gloo.IndexBuffer(self._faces)
        return self._ibo

    def _attach(self, visual):
        super(XYPosComponent, self)._attach(visual)
        visual._program['local_position'] = self.shader_func
        
    def _detach(self, visual):
        super(XYPosComponent, self)._detach(visual)
        visual._program['local_position'] = None
        
    def activate(self, program, draw_mode):
        self.shader_func['xy_pos'] = ('attribute', 'vec2', self.vbo)
        self.shader_func['z_pos'] = ('uniform', 'float', self._z)

    @property
    def index(self):
        if self._faces is False:
            return None
        else:
            return self.ibo

    

class XYZPosComponent(MeshComponent):
    """
    generate local coordinate from xyz (vec3) attribute
    """
    CODE = """
        vec4 $input_xyz_pos() {
            return vec4($xyz_pos, 1.0);
        }
        """

    def __init__(self, pos=None, faces=None):
        super(XYZPosComponent, self).__init__()
        self.shader_func = Function(self.CODE)
        self._pos = None
        self._faces = False
        self._vbo = None
        self._ibo = None
        self.set_data(pos, faces)

    @property
    def supported_draw_modes(self):
        # TODO: Add support for converting between pre-indexed and unindexed
        if self._faces is False:
            return (self.DRAW_PRE_INDEXED,)
        else:
            return (self.DRAW_UNINDEXED,)

    def set_data(self, pos=None, faces=None):
        if pos is not None:
            self._pos = pos
        if faces is not None:
            self._faces = faces
        # TODO: might be better to re-upload data rather than creating
        # a new VB, if possible.
        self._vbo = None
        self.update()

    @property
    def vbo(self):
        if self._vbo is None:
            self._vbo = gloo.VertexBuffer(self._pos)
        return self._vbo

    @property
    def ibo(self):
        if self._ibo is None:
            self._ibo = gloo.IndexBuffer(self._faces)
        return self._ibo
    
    def _attach(self, visual):
        super(XYZPosComponent, self)._attach(visual)
        visual._program['local_position'] = self.shader_func
        
    def _detach(self, visual):
        super(XYZPosComponent, self)._detach(visual)
        visual._program['local_position'] = None
        
    def activate(self, program, draw_mode):
        self.shader_func['xyz_pos'] = ('attribute', 'vec3', self.vbo)
        
    @property
    def index(self):
        if self._faces is False:
            return None
        else:
            return self.ibo


class SurfacePosComponent(MeshComponent):
    """
    Generate local coordinate from 1D z-position.
    
    x,y will be generated in the vertex shader using uniforms that specify the
    range.
    """
    CODE = """
        vec4 $input_z_pos() {
            int xind = int($index % $x_size);
            float x = $x_min + (xind * $x_step);
            int yind = int($index % $y_size);
            float y = $y_min + (yind * $y_step);
            return vec4(x, y, $z_pos, 1.0);
        }
        """

    def __init__(self, z=None):
        super(SurfacePosComponent, self).__init__()
        self.shader_func = Function(self.CODE)
        self._z = None
        self._vbo = None
        if z is not None:
            self.set_data(z)

    @property
    def supported_draw_modes(self):
        # TODO: add support for pre-indexed data
        # (possibly here, possibly in another component class?)
        return (self.DRAW_UNINDEXED,)

    def set_data(self, z):
        if self._z is None or self._z.shape != z.shape:
            # if this data has a new shape, we need a new index buffer
            self._ibo = None
            
        self._z = z
        # TODO: might be better to re-upload data rather than creating
        # a new VB, if possible.
        self._vbo = None
        
        self.update()

    @property
    def vbo(self):
        if self._vbo is None:
            self._vbo = gloo.VertexBuffer(self._z)
            self._index = gloo.VertexBuffer(np.arange(self._z.size))
        return self._vbo

    def _attach(self, visual):
        super(SurfacePosComponent, self)._attach(visual)
        visual._program['local_position'] = self.shader_func
        
    def _detach(self, visual):
        super(SurfacePosComponent, self)._detach(visual)
        visual._program['local_position'] = None
        
    def activate(self, program, draw_mode):
        self.shader_func['z_pos'] = ('attribute', 'vec3', self.vbo)
        
    @property
    def index(self):
        """
        The IndexBuffer used by this input component.        
        """
        if self._ibo is None:
            cols = self._z.shape[1]-1
            rows = self._z.shape[0]-1
            faces = np.empty((cols*rows*2, 3), dtype=np.uint)
            rowtemplate1 = (np.arange(cols).reshape(cols, 1) + 
                            np.array([[0, 1, cols+1]]))
            rowtemplate2 = (np.arange(cols).reshape(cols, 1) + 
                            np.array([[cols+1, 1, cols+2]]))
            for row in range(rows):
                start = row * cols * 2 
                faces[start:start+cols] = rowtemplate1 + row * (cols+1)
                faces[start+cols:start+(cols*2)] = (rowtemplate2 + 
                                                    row * (cols+1))
            self._ibo = gloo.IndexBuffer(faces)
        return self._ibo


class UniformColorComponent(MeshComponent):
    CODE = """
        vec4 $colorInput() {
            return $rgba;
        }
        """
    
    def __init__(self, color=(1,1,1,1)):
        self.shader_func = Function(self.CODE)
        self._color = color
        
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, c):
        self._color = c
        
    def _attach(self, visual):
        super(UniformColorComponent, self)._attach(visual)
        visual._program.add_callback('frag_color', self.shader_func)
        
    def _detach(self):
        self.visual._program.remove_callback('frag_color', self.shader_func)
        super(UniformColorComponent, self)._detach()
        
    def activate(self, program, mode):
        self.shader_func['rgba'] = ('uniform', 'vec4', np.array(self._color))

    @property
    def supported_draw_modes(self):
        return (self.DRAW_PRE_INDEXED, self.DRAW_UNINDEXED)


class VertexColorComponent(MeshComponent):
    FRAG_CODE = """
        vec4 $colorInput() {
            return $rgba;
        }
        """
    
    VERT_CODE = """
        void $colorInputSupport() {
            $output_color = $input_color;
        }
        """
    
    def __init__(self, color=None):
        self.frag_func = Function(self.FRAG_CODE)
        self.vert_func = Function(self.VERT_CODE)
        self._color = color
        self._vbo = None
        
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, c):
        self._color = c
        
    @property
    def vbo(self):
        if self._vbo is None:
            self._vbo = gloo.VertexBuffer(self._color)
        return self._vbo
        
    def _attach(self, visual):
        super(VertexColorComponent, self)._attach(visual)
        visual._program.add_callback('frag_color', self.frag_func)
        visual._program.add_callback('vert_post_hook', self.vert_func)
        
    def _detach(self, visual):
        self.visual._program.remove_callback('frag_color', self.frag_func)
        self.visual._program.remove_callback('vert_post_hook', self.vert_func)
        super(VertexColorComponent, self)._detach()
        
    def activate(self, program, mode):
        # explicitly declare a new variable (to be shared)
        # TODO: does this need to be explicit?
        self.frag_func['rgba'] = ('varying', 'vec4')   
        self.vert_func['input_color'] = ('attribute', 'vec4', self.vbo)
        
        # automatically assign same variable to both
        self.vert_func['output_color'] = self.frag_func['rgba']

    @property
    def supported_draw_modes(self):
        return (self.DRAW_PRE_INDEXED, self.DRAW_UNINDEXED)



class GridContourComponent(MeshComponent):
    FRAG_CODE = """
        vec4 $grid_contour(vec4 color) {
            if ( mod($pos.x, 0.1) < 0.005 ||
                 mod($pos.y, 0.1) < 0.005 || 
                 mod($pos.z, 0.1) < 0.005 ) {
               return vec4(1,1,1,1);
            }
            else {
                return color;
            }
        }
        """
    
    VERT_CODE = """
        void $grid_contour_support() {
            $output_pos = local_position();
        }
        """
    
    def __init__(self, spacing):
        self.frag_func = Function(self.FRAG_CODE)
        self.vert_func = Function(self.VERT_CODE)
        self.spacing = spacing
        
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, c):
        self._color = c
        
    def _attach(self, visual):
        super(GridContourComponent, self)._attach(visual)
        visual._program.add_callback('frag_color', self.frag_func)
        visual._program.add_callback('vert_post_hook', self.vert_func)
        
    def _detach(self, visual):
        self.visual._program.remove_callback('frag_color', self.frag_func)
        self.visual._program.remove_callback('vert_post_hook', self.vert_func)
        super(GridContourComponent, self)._detach()
        
    def activate(self, program, mode):
        self.frag_func['pos'] = ('varying', 'vec4')
        
        # automatically assign same variable to both
        self.vert_func['output_pos'] = self.frag_func['pos']

    @property
    def supported_draw_modes(self):
        return (self.DRAW_PRE_INDEXED, self.DRAW_UNINDEXED)


class ShadingComponent(MeshComponent):
    FRAG_CODE = """
        vec4 $shading(vec4 color) {
            vec3 norm = normalize($normal().xyz);
            vec3 light = normalize($light_direction.xyz);
            float p = dot(light, norm);
            p = (p < 0. ? 0. : p);
            vec4 diffuse = $light_color * p;
            diffuse.a = 1.0;
            p = dot(reflect(light, norm), vec3(0,0,1));
            if (p < 0.0) {
                p = 0.0;
            }
            vec4 specular = $light_color * 5.0 * pow(p, 50.);
            return color * ($ambient + diffuse) + specular;
        }
        """
    
    def __init__(self, normal_comp, lights, ambient=0.2):
        self.frag_func = Function(self.FRAG_CODE)
        self.normal_comp = normal_comp
        self.lights = lights
        self.ambient = ambient
        
    def _attach(self, visual):
        super(ShadingComponent, self)._attach(visual)
        visual._program.add_callback('frag_color', self.frag_func)
        
    def _detach(self, visual):
        self.visual._program.remove_callback('frag_color', self.frag_func)
        super(ShadingComponent, self)._detach()
        
    def activate(self, program, mode):
        # Normals are generated by output of another component
        self.frag_func['normal'] = self.normal_comp.normal_shader()
        
        # TODO: add support for multiple lights
        self.frag_func['light_direction'] = ('uniform', 'vec4', tuple(self.lights[0][0][:3]) + (1,))
        self.frag_func['light_color'] = ('uniform', 'vec4', tuple(self.lights[0][1][:3]) + (1,))
        self.frag_func['ambient'] = ('uniform', 'float', self.ambient)
        

    @property
    def supported_draw_modes(self):
        return (self.DRAW_PRE_INDEXED, self.DRAW_UNINDEXED)


class VertexNormalComponent(MeshComponent):
    FRAG_CODE = """
        vec4 $normal() {
            return $norm;
        }
        """
    
    VERT_CODE = """
        void $normal_support() {
            vec4 o = vec4(0,0,0,1);
            vec4 i = o + $input_normal;
            $output_normal = map_local_to_nd(i) - map_local_to_nd(o);
        }
        """
    
    def __init__(self, meshdata):
        self.frag_func = Function(self.FRAG_CODE)
        self.vert_func = Function(self.VERT_CODE)
        self._meshdata = meshdata
        self._vbo = None
        self._vbo_mode = None
        
    def _make_vbo(self, mode):
        if self._vbo is None or self._vbo_mode != mode:
            if mode is self.DRAW_PRE_INDEXED:
                norm = self._meshdata.vertexNormals(indexed='faces')
            else:
                norm = self._meshdata.vertexNormals()
            self._vbo = gloo.VertexBuffer(norm)
            self._vbo_mode = mode
        return self._vbo
        
    def _attach(self, visual):
        super(VertexNormalComponent, self)._attach(visual)
        visual._program.add_callback('vert_post_hook', self.vert_func)
        # don't attach the fragment function now; other components 
        # will call it.
        
    def _detach(self, visual):
        self.visual._program.remove_callback('vert_post_hook', self.vert_func)
        super(VertexNormalComponent, self)._detach()
        
    def normal_shader(self):
        """
        Return the fragment shader function that returns a normal vector.        
        """
        return self.frag_func
        
    def activate(self, program, mode):
        # explicitly declare a new variable (to be shared)
        # TODO: does this need to be explicit?
        self.frag_func['norm'] = ('varying', 'vec4')   
        self.vert_func['input_normal'] = ('attribute', 'vec4', 
                                          self._make_vbo(mode))
        
        # automatically assign same variable to both
        self.vert_func['output_normal'] = self.frag_func['norm']

    @property
    def supported_draw_modes(self):
        return (self.DRAW_PRE_INDEXED, self.DRAW_UNINDEXED)

