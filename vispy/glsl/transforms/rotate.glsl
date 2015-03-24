// -----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier
// Distributed under the (new) BSD License. See LICENSE.txt for more info.
// -----------------------------------------------------------------------------
uniform vec3 rotate_axis;
uniform vec3 rotate_origin;
uniform float rotate_angle;
uniform mat4 rotate_forward_matrix;
uniform mat4 rotate_inverse_matrix;

vec2 forward(vec2 position)
{
    vec4 P = vec4(position,0.0,1.0);
    P.xy -= rotate_origin.xy;
    P = rotate_forward_matrix*P;
    P.xy += rotate_origin.xy;
    return P.xy;
}

vec3 forward(vec3 position)
{
    vec4 P = vec4(position,1.0);
    P.xyz -= rotate_origin;
    P = rotate_forward_matrix*P;
    P.xyz += rotate_origin;
    return P.xyz;
}

vec2 inverse(vec2 position)
{
    vec4 P = vec4(position,0.0,1.0);
    P.xy -= rotate_origin.xy;
    P = rotate_inverse_matrix*P;
    P.xy += rotate_origin.xy;
    return P.xy;
}

vec3 inverse(vec3 position)
{
    vec4 P = vec4(position,1.0);
    P.xyz -= rotate_origin;
    P = rotate_inverse_matrix*P;
    P.xyz += rotate_origin;
    return P.xyz;
}
