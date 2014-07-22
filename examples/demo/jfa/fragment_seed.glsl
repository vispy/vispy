// Jump flooding algorithm for EDT according
// to Danielsson (1980) and Guodong Rong (2007).
// Implementation by Stefan Gustavson 2010.
// This code is in the public domain.

// This shader initializes the distance field
// in preparation for the flood filling.

uniform sampler2D texture;
varying float stepu;
varying float stepv;
varying vec2 uv;

void main( void )
{
  float pixel = texture2D(texture, uv).r;
  vec4 myzero = vec4(128. / 255., 128. / 255., 0., 0.);  // Zero
  vec4 myinfinity = vec4(0., 0., 0., 0.);                // Infinity
  // Pixels > 0.5 are objects, others are background
  gl_FragColor = pixel > 0.5 ? myinfinity : myzero;
}
