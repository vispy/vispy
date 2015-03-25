// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
//
//   Polar projection
//   See http://en.wikipedia.org/wiki/Hammer_projection
//
// ----------------------------------------------------------------------------
#include "math/constants.glsl"

uniform float polar_origin;

vec4 forward(float rho, float theta, float z, float w)
{
    return vec4(rho * cos(theta + polar_origin),
                rho * sin(theta + polar_origin),
                z, w);
}
vec4 forward(float x, float y) {return forward(x, y, 0.0, 1.0);}
vec4 forward(float x, float y, float z) {return forward(x, y, z, 1.0);}
vec4 forward(vec2 P) { return forward(P.x, P.y); }
vec4 forward(vec3 P) { return forward(P.x, P.y, P.z, 1.0); }
vec4 forward(vec4 P) { return forward(P.x, P.y, P.z, P.w); }
// vec4 forward(float x, float y, float z) { return vec3(forward(x,y),z); }

vec4 inverse(float x, float y, float z, float w)
{
    float rho = length(vec2(x,y));
    float theta = atan(y,x);
    if( theta < 0.0 )
        theta = 2.0*M_PI+theta;
    return vec4(rho, theta-polar_origin, z, w);
}
vec4 inverse(float x, float y) {return inverse(x,y,0.0,1.0); }
vec4 inverse(float x, float y, float z) {return inverse(x,y,z,1.0); }
vec4 inverse(vec2 P) { return inverse(P.x, P.y, 0.0, 1.0); }
vec4 inverse(vec3 P) { return inverse(P.x, P.y, P.z, 1.0); }
vec4 inverse(vec4 P) { return inverse(P.x, P.y, P.z, P.w); }

//vec3 inverse(float x, float y, float z) { return vec3(inverse(x,y),z); }
