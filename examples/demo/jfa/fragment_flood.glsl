// Jump flooding algorithm for EDT according
// to Danielsson (1980) and Guodong Rong (2007).
// Implementation by Stefan Gustavson 2010.
// This code is in the public domain.

// This code represents one iteration of the flood filling.
// You need to run it multiple times with different step
// lengths to perform a full distance transformation.

uniform sampler2D texture;
varying float stepu;
varying float stepv;
varying vec2 uv;

// Helper functions to remap unsigned normalized floats [0.0,1.0]
// coming from an integer texture to the range we need [-1, 1].
// The transformations are very specifically designed to map
// integer texel values exactly to pixel centers, and vice versa.
// (See fragment_seed.glsl for details.)

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
  vec3 newseed; // Closest point from that candidate (.xy) and its distance (.z)
  vec3 bestseed; // Closest seed so far
  bestseed.xy = remap(texture2D(texture, uv).rgba);
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

  stepvec = vec2(-stepu, -stepv);
  newvec = uv + stepvec;
  if ( all( bvec4( lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0)) ) ) ) {
    newseed.xy = remap(texture2D(texture, newvec).rgba);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate distance"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
  }

  stepvec = vec2(-stepu, 0.0);
  newvec = uv + stepvec;
  if ( all( bvec4( lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0)) ) ) ) {
    newseed.xy = remap(texture2D(texture, newvec).rgba);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate distance"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
  }

  stepvec = vec2(-stepu, stepv);
  newvec = uv + stepvec;
  if ( all( bvec4( lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0)) ) ) ) {
    newseed.xy = remap(texture2D(texture, newvec).rgba);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate distance"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
  }

  stepvec = vec2(0.0, -stepv);
  newvec = uv + stepvec;
  if ( all( bvec4( lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0)) ) ) ) {
    newseed.xy = remap(texture2D(texture, newvec).rgba);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate distance"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
  }

  stepvec = vec2(0.0, stepv);
  newvec = uv + stepvec;
  if ( all( bvec4( lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0)) ) ) ) {
    newseed.xy = remap(texture2D(texture, newvec).rgba);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate distance"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
  }

  stepvec = vec2(stepu, -stepv);
  newvec = uv + stepvec;
  if ( all( bvec4( lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0)) ) ) ) {
    newseed.xy = remap(texture2D(texture, newvec).rgba);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate distance"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
  }

  stepvec = vec2(stepu, 0.0);
  newvec = uv + stepvec;
  if ( all( bvec4( lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0)) ) ) ) {
    newseed.xy = remap(texture2D(texture, newvec).rgba);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate distance"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
  }

  stepvec = vec2(stepu, stepv);
  newvec = uv + stepvec;
  if ( all( bvec4( lessThan(newvec, vec2(1.0)), greaterThan(newvec, vec2(0.0)) ) ) ) {
    newseed.xy = remap(texture2D(texture, newvec).rgba);
    if(newseed.x > -0.99999) { // if the new seed is not "indeterminate distance"
      newseed.xy = newseed.xy + stepvec;
      newseed.z = length(newseed.xy);
      if(newseed.z < bestseed.z) {
        bestseed = newseed;
      }
    }
  }

  gl_FragColor = remap_inv(bestseed.xy);
}
