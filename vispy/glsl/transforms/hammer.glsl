// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
//
//   Hammer projection
//   See http://en.wikipedia.org/wiki/Hammer_projection
//
// ----------------------------------------------------------------------------
#include "math/constants.glsl"

const float B = 2.0;

vec4 forward(float longitude, float latitude, float z, float w)
{
    float cos_lat = cos(latitude);
    float sin_lat = sin(latitude);
    float cos_lon = cos(longitude/B);
    float sin_lon = sin(longitude/B);
    float d = sqrt(1.0 + cos_lat * cos_lon);
    float x = (B * M_SQRT2 * cos_lat * sin_lon) / d;
    float y =     (M_SQRT2 * sin_lat) / d;
    return vec4(x,y,z,w);
}
vec4 forward(float x, float y) {return forward(x, y, 0.0, 1.0);}
vec4 forward(float x, float y, float z) {return forward(x, y, 0.0, 1.0);}
vec4 forward(vec2 P) { return forward(P.x, P.y); }
vec4 forward(vec3 P) { return forward(P.x, P.y, P.z, 1.0); }
vec4 forward(vec4 P) { return forward(P.x, P.y, P.z, P.w); }


vec2 inverse(float x, float y)
{
    float z = 1.0 - (x*x/16.0) - (y*y/4.0);
    // if (z < 0.0)
    //     discard;
    z = sqrt(z);
    float longitude = 2.0*atan( (z*x),(2.0*(2.0*z*z - 1.0)));
    float latitude = asin(z*y);
    return vec2(longitude, latitude);
}
vec2 inverse(vec2 P) { return inverse(P.x,P.y); }
vec3 inverse(vec3 P) { return vec3(inverse(P.x,P.y), P.z); }
vec4 inverse(vec4 P) { return vec4(inverse(P.x,P.y), P.z, P.w); }
