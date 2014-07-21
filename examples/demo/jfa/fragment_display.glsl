// Jump flooding algorithm for EDT according
// to Danielsson (1980) and Guodong Rong (2007).
// Implementation by Stefan Gustavson 2010.
// This code is in the public domain.

// This shader displays the final distance field
// visualized as an RGB image.

uniform sampler2D texture;
uniform float texlevels;
varying vec2 uv;

vec2 remap(vec2 floatdata) {
     return floatdata * (texlevels-1.0) / texlevels * 2.0 - 1.0;
}

void main( void )
{
  vec2 distvec = remap(texture2D(texture, uv).rg);
  vec2 rainbow = 0.5+0.5*(normalize(distvec));
  gl_FragColor = vec4(rainbow, 1.0-length(distvec)*4.0, 1.0);
}
