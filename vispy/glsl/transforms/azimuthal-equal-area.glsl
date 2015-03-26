// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------

float scale(float x) { return sqrt(2.0/(1.0+x)); }
float angle(float x) { return 2.0 * asin(x/2.0); }

vec2 forward(float longitude, float latitude)
{
    float cos_lon = cos(longitude);
    float cos_lat = cos(latitude);
    float k = scale(cos_lon * cos_lat);
    return vec2( k * cos_lat * sin(longitude), k * sin(latitude));
}
vec2 forward(vec2 P) { return forward(P.x,P.y); }
vec3 forward(vec3 P) { return vec3(forward(P.x,P.y), P.z); }
vec4 forward(vec4 P) { return vec4(forward(P.x,P.y), P.z, P.w); }

vec2 inverse(float x, float y)
{
    float rho = sqrt(x*x + y*y);
    float c = angle(rho);
    float sinc = sin(c);
    float cosc = cos(c);
    if (rho != 0)
        return vec2( atan(x*sinc, rho*cosc), asin(y*sinc/rho));
    return vec2( atan(x*sinc, rho*cosc), asin(0));
}
vec2 inverse(vec2 P) { return inverse(P.x,P.y); }
vec3 inverse(vec3 P) { return vec3(inverse(P.x,P.y), P.z); }
vec4 inverse(vec4 P) { return vec4(inverse(P.x,P.y), P.z, P.w); }
