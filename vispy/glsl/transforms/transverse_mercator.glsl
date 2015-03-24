// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
//
//   Transverse Mercator projection
//   See http://en.wikipedia.org/wiki/Transverse_Mercator_projection
//
// ----------------------------------------------------------------------------
#include "math/constants.glsl"

// Constants
const float k0 = 0.75;
const float a  = 1.00;

// Helper functions
float cosh(float x) { return 0.5 * (exp(x)+exp(-x)); }
float sinh(float x) { return 0.5 * (exp(x)-exp(-x)); }

vec2 forward(float lambda, float phi)
{
    float x = 0.5*k0*log((1.0+sin(lambda)*cos(phi)) / (1.0 - sin(lambda)*cos(phi)));
    float y = k0*a*atan(tan(phi), cos(lambda));
    return vec2(x,y);
}
vec2 forward(vec2 P) { return forward(P.x,P.y); }
vec3 forward(vec3 P) { return vec3(forward(P.x,P.y), P.z); }
vec4 forward(vec4 P) { return vec4(forward(P.x,P.y), P.z, P.w); }

vec2 inverse(float x, float y)
{
    float lambda = atan(sinh(x/(k0*a)),cos(y/(k0*a)));
    float phi    = asin(sin(y/(k0*a))/cosh(x/(k0*a)));
    return vec2(lambda,phi);
}
vec2 inverse(vec2 P) { return inverse(P.x,P.y); }
vec3 inverse(vec3 P) { return vec3(inverse(P.x,P.y), P.z); }
vec4 inverse(vec4 P) { return vec4(inverse(P.x,P.y), P.z, P.w); }
