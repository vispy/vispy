// Jump flooding algorithm for EDT according
// to Danielsson (1980) and Guodong Rong (2007).
// Implementation by Stefan Gustavson 2010.
// This code is in the public domain.

// This shader displays the final distance field
// visualized as an RGB image.

uniform sampler2D texture;
varying vec2 uv;

vec2 remap(vec4 floatdata) {
    vec2 scaled_data = vec2(floatdata.x * 65280. + floatdata.z * 255.,
                            floatdata.y * 65280. + floatdata.w * 255.);
    return scaled_data / 32768. - 1.0;
}

void main( void )
{
  vec2 distvec = remap(texture2D(texture, uv).rgba);
  vec2 rainbow = 0.5+0.5*(normalize(distvec));
  gl_FragColor = vec4(rainbow, 1.0-length(distvec)*4.0, 1.0);
}
