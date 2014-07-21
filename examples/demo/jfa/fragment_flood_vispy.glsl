// Jump flooding algorithm for EDT according
// to Danielsson (1980) and Guodong Rong (2007).
// Implementation by Stefan Gustavson 2010.
// This code is in the public domain.

// This code represents one iteration of the flood filling.
// You need to run it multiple times with different step
// lengths to perform a full distance transformation.

uniform sampler2D u_texture;
uniform float u_texlevels;
varying float v_stepu;
varying float v_stepv;
varying vec2 v_texcoord;

// Helper functions to remap unsigned normalized floats [0.0,1.0]
// coming from an integer texture to the range we need [-1, 1].
// The transformations are very specifically designed to map
// integer texel values exactly to pixel centers, and vice versa.
// (See fragment_seed.glsl for details.)
vec2 remap(vec2 floatdata) {
     return floatdata * (u_texlevels - 1.0) / u_texlevels * 2.0 - 1.0;
}

vec2 remap_inv(vec2 floatvec) {
     return (floatvec + 1.0)* 0.5 * u_texlevels / (u_texlevels - 1.0);
}

void main( void )
{
  // Search for better distance vectors among 8 candidates
  vec2 stepvec; // Relative offset to candidate being tested
  vec2 newvec;  // Absolute position of that candidate
  vec3 newseed; // Closest point from that candidate (.xy) and its distance (.z)
  vec3 bestseed; // Closest seed so far
  vec2 uv = v_texcoord.xy;
  bestseed.xy = remap(texture2D(u_texture, uv).rg);
  bestseed.z = length(bestseed.xy);

  // This code depends on the texture having a CLAMP_TO_BORDER
  // attribute and a border color with R = 0.
  // The commented-out lines handle clamping to the edge explicitly
  // to avoid propagating incorrect vectors when looking outside
  // of [0,1] in u and/or v.
  // These explicit conditionals cause a slowdown of about 25%.
  // Sometimes a periodic transform with edge repeats might be
  // what you want. In that case, the texture wrap mode can be
  // set to GL_REPEAT, and the shader code can be left unchanged.

  stepvec = vec2(-v_stepu, -v_stepv);
  newvec = uv + stepvec;
//  if ( all( bvec4( lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0)) ) ) ) {
    newseed.xy = remap(texture2D(u_texture, newvec).rg);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate distance"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
//  }

  stepvec = vec2(-v_stepu, 0.0);
  newvec = uv + stepvec;
//  if ( all( bvec4( lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0)) ) ) ) {
    newseed.xy = remap(texture2D(u_texture, newvec).rg);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate distance"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
//  }

  stepvec = vec2(-v_stepu, v_stepv);
  newvec = uv + stepvec;
//  if ( all( bvec4( lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0)) ) ) ) {
    newseed.xy = remap(texture2D(u_texture, newvec).rg);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate distance"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
//  }

  stepvec = vec2(0.0, -v_stepv);
  newvec = uv + stepvec;
//  if ( all( bvec4( lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0)) ) ) ) {
    newseed.xy = remap(texture2D(u_texture, newvec).rg);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate distance"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
//  }

  stepvec = vec2(0.0, v_stepv);
  newvec = uv + stepvec;
//  if ( all( bvec4( lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0)) ) ) ) {
    newseed.xy = remap(texture2D(u_texture, newvec).rg);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate distance"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
//  }

  stepvec = vec2(v_stepu, -v_stepv);
  newvec = uv + stepvec;
//  if ( all( bvec4( lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0)) ) ) ) {
    newseed.xy = remap(texture2D(u_texture, newvec).rg);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate distance"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
//  }

  stepvec = vec2(v_stepu, 0.0);
  newvec = uv + stepvec;
//  if ( all( bvec4( lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0)) ) ) ) {
    newseed.xy = remap(texture2D(u_texture, newvec).rg);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate distance"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
//  }

  stepvec = vec2(v_stepu, v_stepv);
  newvec = uv + stepvec;
//  if ( all( bvec4( lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0)) ) ) ) {
    newseed.xy = remap(texture2D(u_texture, newvec).rg);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate distance"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
//  }

  gl_FragColor = vec4(remap_inv(bestseed.xy), 0.0, 1.0);
}
