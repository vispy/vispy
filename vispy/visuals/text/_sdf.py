# -*- coding: utf-8 -*-
"""
Jump flooding algoritm for EDT using GLSL code:
Author: Stefan Gustavson (stefan.gustavson@gmail.com)
2010-08-24. This code is in the public domain.

Adapted to `vispy` by Eric Larson <larson.eric.d@gmail.com>.
"""

import numpy as np
from os import path as op
from ...gloo import (Program, FrameBuffer, VertexBuffer, Texture2D, 
                     set_viewport, set_state)

this_dir = op.dirname(__file__)

vert_seed = """
attribute vec2 a_position;
attribute vec2 a_texcoord;
varying vec2 v_uv;

void main( void )
{
  v_uv = a_texcoord.xy;
  gl_Position = vec4(a_position.xy, 0., 1.);
}
"""

vert = """
uniform float u_texw;
uniform float u_texh;
uniform float u_step;
attribute vec2 a_position;
attribute vec2 a_texcoord;
varying float v_stepu;
varying float v_stepv;
varying vec2 v_uv;

void main( void )
{
  v_uv = a_texcoord.xy;
  v_stepu = u_step / u_texw; // Saves a division in the fragment shader
  v_stepv = u_step / u_texh;
  gl_Position = vec4(a_position.xy, 0., 1.);
}
"""

frag_seed = """
uniform sampler2D u_texture;
varying vec2 v_uv;

void main( void )
{
  float pixel = texture2D(u_texture, v_uv).r;
  vec4 myzero = vec4(128. / 255., 128. / 255., 0., 0.);  // Zero
  vec4 myinfinity = vec4(0., 0., 0., 0.);                // Infinity
  // Pixels >= 0.5 are objects, others are background
  gl_FragColor = pixel >= 0.5 ? myzero : myinfinity;
}
"""

frag_flood = """
uniform sampler2D u_texture;
varying float v_stepu;
varying float v_stepv;
varying vec2 v_uv;

vec2 remap(vec4 floatdata) {
    vec2 scaleddata = vec2(floatdata.x * 65280. + floatdata.z * 255.,
                           floatdata.y * 65280. + floatdata.w * 255.);
    return scaleddata / 32768. - 1.0;
}

vec4 remap_inv(vec2 floatvec) {
    vec2 data = (floatvec + 1.0) * 32768.;
    float x = floor(data.x / 256.);
    float y = floor(data.y / 256.);
    return vec4(x, y, data.x - x * 256., data.y - y * 256.) / 255.;
}

void main( void )
{
  // Search for better distance vectors among 8 candidates
  vec2 stepvec; // Relative offset to candidate being tested
  vec2 newvec;  // Absolute position of that candidate
  vec3 newseed; // Closest point from that candidate (.xy) and its dist (.z)
  vec3 bestseed; // Closest seed so far
  bestseed.xy = remap(texture2D(u_texture, v_uv).rgba);
  bestseed.z = length(bestseed.xy);

  stepvec = vec2(-v_stepu, -v_stepv);
  newvec = v_uv + stepvec;
  if (all(bvec4(lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0))))){
    newseed.xy = remap(texture2D(u_texture, newvec).rgba);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate dist"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
  }

  stepvec = vec2(-v_stepu, 0.0);
  newvec = v_uv + stepvec;
  if (all(bvec4(lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0))))){
    newseed.xy = remap(texture2D(u_texture, newvec).rgba);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate dist"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
  }

  stepvec = vec2(-v_stepu, v_stepv);
  newvec = v_uv + stepvec;
  if (all(bvec4(lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0))))){
    newseed.xy = remap(texture2D(u_texture, newvec).rgba);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate dist"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
  }

  stepvec = vec2(0.0, -v_stepv);
  newvec = v_uv + stepvec;
  if (all(bvec4(lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0))))){
    newseed.xy = remap(texture2D(u_texture, newvec).rgba);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate dist"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
  }

  stepvec = vec2(0.0, v_stepv);
  newvec = v_uv + stepvec;
  if (all(bvec4(lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0))))){
    newseed.xy = remap(texture2D(u_texture, newvec).rgba);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate dist"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
  }

  stepvec = vec2(v_stepu, -v_stepv);
  newvec = v_uv + stepvec;
  if (all(bvec4(lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0))))){
    newseed.xy = remap(texture2D(u_texture, newvec).rgba);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate dist"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
  }

  stepvec = vec2(v_stepu, 0.0);
  newvec = v_uv + stepvec;
  if (all(bvec4(lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0))))){
    newseed.xy = remap(texture2D(u_texture, newvec).rgba);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate dist"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
  }

  stepvec = vec2(v_stepu, v_stepv);
  newvec = v_uv + stepvec;
  if (all(bvec4(lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0))))){
    newseed.xy = remap(texture2D(u_texture, newvec).rgba);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate dist"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
  }

  gl_FragColor = remap_inv(bestseed.xy);
}
"""

frag_insert = """

uniform sampler2D u_texture;
uniform sampler2D u_pos_texture;
uniform sampler2D u_neg_texture;
varying float v_stepu;
varying float v_stepv;
varying vec2 v_uv;

vec2 remap(vec4 floatdata) {
    vec2 scaled_data = vec2(floatdata.x * 65280. + floatdata.z * 255.,
                            floatdata.y * 65280. + floatdata.w * 255.);
    return scaled_data / 32768. - 1.0;
}

void main( void )
{
    float pixel = texture2D(u_texture, v_uv).r;
    // convert distance from normalized units -> pixels
    vec2 rescale = vec2(v_stepu, v_stepv);
    float shrink = 8.;
    rescale = rescale * 256. / shrink;
    // Without the division, 1 RGB increment = 1 px distance
    vec2 pos_distvec = remap(texture2D(u_pos_texture, v_uv).rgba) / rescale;
    vec2 neg_distvec = remap(texture2D(u_neg_texture, v_uv).rgba) / rescale;
    if (pixel <= 0.5)
        gl_FragColor = vec4(0.5 - length(pos_distvec));
    else
        gl_FragColor = vec4(0.5 - (shrink - 1.) / 256. + length(neg_distvec));
}
"""


class SDFRenderer(object):
    def __init__(self):
        self.program_seed = Program(vert_seed, frag_seed)
        self.program_flood = Program(vert, frag_flood)
        self.program_insert = Program(vert, frag_insert)
        self.programs = [self.program_seed, self.program_flood,
                         self.program_insert]

        # Initialize variables
        self.fbo_to = [FrameBuffer(), FrameBuffer(), FrameBuffer()]
        vtype = np.dtype([('a_position', np.float32, 2),
                          ('a_texcoord', np.float32, 2)])
        vertices = np.zeros(4, dtype=vtype)
        vertices['a_position'] = [[-1., -1.], [-1., 1.], [1., -1.], [1., 1.]]
        vertices['a_texcoord'] = [[0., 0.], [0., 1.], [1., 0.], [1., 1.]]
        vertices = VertexBuffer(vertices)
        self.program_insert['u_step'] = 1.
        for program in self.programs:
            program.bind(vertices)

    def render_to_texture(self, data, texture, offset, size):
        """Render a SDF to a texture at a given offset and size

        Parameters
        ----------
        data : array
            Must be 2D with type np.ubyte.
        texture : instance of Texture2D
            The texture to render to.
        offset : tuple of int
            Offset (x, y) to render to inside the texture.
        size : tuple of int
            Size (w, h) to render inside the texture.
        """
        assert isinstance(texture, Texture2D)
        set_state(blend=False, depth_test=False)

        # calculate the negative half (within object)
        orig_tex = Texture2D(255 - data, format='luminance', 
                             wrapping='clamp_to_edge', interpolation='nearest')
        edf_neg_tex = self._render_edf(orig_tex)

        # calculate positive half (outside object)
        orig_tex[:, :, 0] = data
        
        edf_pos_tex = self._render_edf(orig_tex)

        # render final product to output texture
        self.program_insert['u_texture'] = orig_tex
        self.program_insert['u_pos_texture'] = edf_pos_tex
        self.program_insert['u_neg_texture'] = edf_neg_tex
        self.fbo_to[-1].color_buffer = texture
        with self.fbo_to[-1]:
            set_viewport(tuple(offset) + tuple(size))
            self.program_insert.draw('triangle_strip')

    def _render_edf(self, orig_tex):
        """Render an EDF to a texture"""
        # Set up the necessary textures
        sdf_size = orig_tex.shape[:2]

        comp_texs = []
        for _ in range(2):
            tex = Texture2D(sdf_size + (4,), format='rgba',
                            interpolation='nearest', wrapping='clamp_to_edge')
            comp_texs.append(tex)
        self.fbo_to[0].color_buffer = comp_texs[0]
        self.fbo_to[1].color_buffer = comp_texs[1]
        for program in self.programs[1:]:  # program_seed does not need this
            program['u_texh'], program['u_texw'] = sdf_size

        # Do the rendering
        last_rend = 0
        with self.fbo_to[last_rend]:
            set_viewport(0, 0, sdf_size[1], sdf_size[0])
            self.program_seed['u_texture'] = orig_tex
            self.program_seed.draw('triangle_strip')
        stepsize = (np.array(sdf_size) // 2).max()
        while stepsize > 0:
            self.program_flood['u_step'] = stepsize
            self.program_flood['u_texture'] = comp_texs[last_rend]
            last_rend = 1 if last_rend == 0 else 0
            with self.fbo_to[last_rend]:
                set_viewport(0, 0, sdf_size[1], sdf_size[0])
                self.program_flood.draw('triangle_strip')
            stepsize //= 2
        return comp_texs[last_rend]
