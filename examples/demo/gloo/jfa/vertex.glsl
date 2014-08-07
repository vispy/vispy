// Jump flooding algorithm for EDT according
// to Danielsson (1980) and Guodong Rong (2007).
// Implementation by Stefan Gustavson 2010.
// This code is in the public domain.

// This code represents one iteration of the flood filling.
// You need to run it multiple times with different step
// lengths to perform a full distance transformation.

uniform float texw;
uniform float texh;
uniform float step;
varying float stepu;
varying float stepv;
varying vec2 uv;

void main( void )
{
  // Get the texture coordinates
  uv = gl_MultiTexCoord0.xy;
  stepu = step / texw; // Saves a division in the fragment shader
  stepv = step / texh;
  gl_Position = ftransform();
}
