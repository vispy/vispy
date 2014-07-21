// Jump flooding algorithm for EDT according
// to Danielsson (1980) and Guodong Rong (2007).
// Implementation by Stefan Gustavson 2010.
// This code is in the public domain.

// This shader initializes the distance field
// in preparation for the flood filling.

uniform sampler2D texture;
uniform float texlevels;
varying float stepu, stepv; // Unused here
varying vec2 uv;

// Helper function to remap unsigned normalized floats [0.0..1.0]
// coming from a texture stored in integer format internally to a
// signed float vector pointing exactly to a pixel centre in texture
// space. The range of valid vectors is
// [-1.0+0.5/texsize, 1.0-0.5/texsize], with the special value
// -1.0-0.5*texsize (represented as integer 0) meaning
// "distance vector still undetermined".
// The mapping is carefully designed to map both 8 bit and 16
// bit integer texture data to distinct and exact floating point
// texture coordinate offsets and vice versa.
// 8 bit integer textures can be used to transform images up to
// size 128x128 pixels, and 16 bit integer textures can be used to
// transform images up to 32768x32768, i.e. beyond the largest
// texture size available in current implementations of OpenGL.
// Direct use of integers in the shader (by means of texture2DRect
// and GL_RG8I and GL_RG16I texture formats) could be faster, but
// this code is conveniently compatible even with version 1.2 of GLSL
// (i.e. OpenGL 2.1), and the main shader is limited by texture access
// and branching, not ALU capacity, so a few extra multiplications
// for indexing and output storage are not that bad.
vec2 remap(vec2 floatdata) {
     return floatdata * (texlevels-1.0) / texlevels * 2.0 - 1.0;
}

void main( void )
{
  float pixel = texture2D(texture, uv).r;
  float myzero = 0.5 * texlevels / (texlevels - 1.0); // Represents zero
  float myinfinity = 0.0;                             // Represents infinity
  // Pixels > 0.5 are objects, others are background
  gl_FragColor = vec4(pixel > 0.5 ? myinfinity : myzero);
}
