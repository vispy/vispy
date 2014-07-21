// Jump flooding algorithm for EDT according
// to Danielsson (1980) and Guodong Rong (2007).
// Implementation by Stefan Gustavson 2010.
// This code is in the public domain.

// This code represents one iteration of the flood filling.
// You need to run it multiple times with different step
// lengths to perform a full distance transformation.

uniform float u_texw;
uniform float u_texh;
uniform float u_step;
attribute vec2 a_position;
attribute vec2 a_texcoord;
varying float v_stepu;
varying float v_stepv;
varying vec2 v_texcoord;

void main( void )
{
  // Get the texture coordinates
  v_stepu = u_step / u_texw; // Saves a division in the fragment shader
  v_stepv = u_step / u_texh;
  v_texcoord = a_texcoord;
  gl_Position = vec4(a_position, 0.0, 1.0);
}
