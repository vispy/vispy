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
// Must return the color for this fragment
// or discard.
vec4 frag_color();

// Generic hook for executing code after the fragment color has been set
// Functions in this hook may modify glFragColor or discard.
void frag_post_hook();

void main(void) {
    gl_FragColor = frag_color();
    
    frag_post_hook();
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
        self._program.add_chain('frag_post_hook')
        
        # Components for plugging different types of position and color input.
        self._pos_component = None
        self._color_component = None
        self.pos_component = XYZPosComponent()
        self.color_component = UniformColorComponent()
        
        glopts = kwds.pop('gl_options', 'opaque')
        self.set_gl_options(glopts)
        
        if kwds:
            self.set_data(**kwds)

    def set_data(self, pos, faces=None, z=0.0, color=(1,1,1,1)):
        """
        *pos* must be array of shape (..., 2) or (..., 3).
        *z* is only used in the former case.
        
        *faces* is not supported yet.
        """
        if faces is not None:
            raise NotImplementedError  # stub
      
        # select input component based on pos.shape
        if pos.shape[-1] == 2:
            if not isinstance(self.pos_component, XYPosComponent):
                self.pos_component = XYPosComponent()
            self.pos_component.set_data(xy=pos, z=z)
        elif pos.shape[-1] == 3:
            if not isinstance(self.pos_component, XYZPosComponent):
                self.pos_component = XYZPosComponent()
            self.pos_component.set_data(pos=pos)
            
        if isinstance(color, tuple):
            self.color_component = UniformColorComponent(color)

    def paint(self):
        super(MeshVisual, self).paint()
        
        modes = set(self.pos_component.supported_draw_modes)
        modes &= set(self.color_component.supported_draw_modes)
        if len(modes) == 0:
            raise Exception("Visual cannot paint--no mutually supported "
                            "draw modes between components.")
        
        #TODO: pick most efficient draw mode!
        mode = list(modes)[0]
            
        self.pos_component.activate(self._program, mode)
        self.color_component.activate(self._program, mode)
        
        
        # TODO: this must be optimized.
        self._program['map_local_to_nd'] = self.transform.shader_map()
        
        self._program.draw(gloo.gl.GL_TRIANGLES, self.pos_component.index)

    @property
    def pos_input_component(self):
        return self._pos_input_component

    @pos_input_component.setter
    def pos_input_component(self, component):
        if self._pos_input_component is not None:
            self._pos_input_component._detach(self)
            self._pos_input_component = None
        component._attach(self)
        self._pos_input_component = component
        self.events.update()
        
    # TODO: Allow multiple color components to be added in series
    @property
    def color_input_component(self):
        return self._color_input_component

    @color_input_component.setter
    def color_input_component(self, component):
        if self._color_input_component is not None:
            self._color_input_component._detach(self)
            self._color_input_component = None
        component._attach(self)
        self._color_input_component = component
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
            self.visual.update()

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

    def __init__(self, xy=None, z=0.0):
        super(XYPosComponent, self).__init__()
        self.shader_func = Function(self.CODE)
        self._xy = None
        self._z = 0.0
        self._vbo = None
        self.set_data(xy, z)
        
    @property
    def supported_draw_modes(self):
        # TODO: add support for unindexed data
        # (possibly here, possibly in another component class?)
        return (self.DRAW_PRE_INDEXED,)

    def set_data(self, xy=None, z=None):
        if xy is not None:
            self._xy = xy
        if z is not None:
            self._z = z
        # TODO: might be better to re-upload data rather than creating
        # a new VB, if possible.
        self._vbo = None
        self.update()

    @property
    def vbo(self):
        if self._vbo is None:
            self._vbo = gloo.VertexBuffer(self._xy)
        return self._vbo

    def activate(self, program, draw_mode):
        self.shader_func['xy_pos'] = ('attribute', 'vec2', self.vbo)
        self.shader_func['z_pos'] = ('uniform', 'float', self._z)
        program['local_position'] = self.shader_func

    @property
    def index(self):
        # no indexes supported yet.
        return None


class XYZPosComponent(MeshComponent):
    """
    generate local coordinate from xyz (vec3) attribute
    """
    CODE = """
        vec4 $input_xyz_pos() {
            return vec4($xyz_pos, 1.0);
        }
        """

    def __init__(self, pos=None):
        super(XYZPosComponent, self).__init__()
        self.shader_func = Function(self.CODE)
        self._pos = None
        self._vbo = None
        if pos is not None:
            self.set_data(pos)

    @property
    def supported_draw_modes(self):
        # TODO: add support for unindexed data
        # (possibly here, possibly in another component class?)
        return (self.DRAW_PRE_INDEXED,)

    def set_data(self, pos):
        self._pos = pos
        # TODO: might be better to re-upload data rather than creating
        # a new VB, if possible.
        self._vbo = None
        self.update()

    @property
    def vbo(self):
        if self._vbo is None:
            self._vbo = gloo.VertexBuffer(self._pos)
        return self._vbo

    def activate(self, program, draw_mode):
        self.shader_func['xyz_pos']=('attribute', 'vec3', self.vbo)
        program['local_position'] = self.shader_func
        
    @property
    def index(self):
        # no indexes supported yet.
        return None


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

    def activate(self, program, draw_mode):
        self.shader_func['z_pos']=('attribute', 'vec3', self.vbo)
        program['local_position'] = self.shader_func
        
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
        
    def activate(self, program, mode):
        self.shader_func['rgba'] = ('uniform', 'vec4', np.array(self._color))
        program['frag_color'] = self.shader_func

    @property
    def supported_draw_modes(self):
        return (self.DRAW_PRE_INDEXED, self.DRAW_UNINDEXED)


class MeshColorInputComponent(VisualComponent):
    def __init__(self, visual):
        super(MeshColorInputComponent, self).__init__(visual)
        self.frag_func = Function("""
            vec4 $colorInput() {
                return $rgba;
            }
            """)
        
        self.support_func = Function("""
            void $colorInputSupport() {
                $output_color = $input_color;
            }
            """)
    
    def update(self):
        # Select uniform- or attribute-input 
        program = self.visual._program
        if 'color' in self.visual._data.dtype.fields:
            # explicitly declare a new variable (to be shared)
            # TODO: does this need to be explicit?
            self.frag_func['rgba'] = ('varying', 'vec4')   
            
            program['frag_color'] = self.frag_func
            
            program.add_callback('vert_post_hook', self.support_func)
            self.support_func['input_color'] = ('attribute', 'vec4', self.visual._vbo['color'])
            self.support_func['output_color'] = self.frag_func['rgba'] # automatically assign same variable to both
            
        else:
            self.frag_func['rgba'] = ('uniform', 'vec4', np.array(self.visual._opts['color']))
            program['frag_color'] = self.frag_func
            
    