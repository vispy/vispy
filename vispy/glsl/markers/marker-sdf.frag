// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#version 120

// Constants
// ------------------------------------
const float SQRT_2 = 1.4142135623730951;

// Uniforms
// ------------------------------------
uniform sampler2D u_texture;
uniform vec2 u_texture_shape;

// Varyings
// ------------------------------------
varying float v_antialias;
varying float v_linewidth;
varying vec4  v_fg_color;
varying vec4  v_bg_color;
varying float v_size;
varying vec2  v_rotation;

vec4 Nearest(sampler2D u_data, vec2 u_shape, vec2 v_texcoord);
vec4 Bilinear(sampler2D u_data, vec2 u_shape, vec2 v_texcoord);
vec4 Hanning(sampler2D u_data, vec2 u_shape, vec2 v_texcoord);
vec4 Hamming(sampler2D u_data, vec2 u_shape, vec2 v_texcoord);
vec4 Hermite(sampler2D u_data, vec2 u_shape, vec2 v_texcoord);
vec4 Kaiser(sampler2D u_data, vec2 u_shape, vec2 v_texcoord);
vec4 Quadric(sampler2D u_data, vec2 u_shape, vec2 v_texcoord);
vec4 Bicubic(sampler2D u_data, vec2 u_shape, vec2 v_texcoord);
vec4 CatRom(sampler2D u_data, vec2 u_shape, vec2 v_texcoord);
vec4 Mitchell(sampler2D u_data, vec2 u_shape, vec2 v_texcoord);
vec4 Spline16(sampler2D u_data, vec2 u_shape, vec2 v_texcoord);
vec4 Spline36(sampler2D u_data, vec2 u_shape, vec2 v_texcoord);
vec4 Gaussian(sampler2D u_data, vec2 u_shape, vec2 v_texcoord);
vec4 Bessel(sampler2D u_data, vec2 u_shape, vec2 v_texcoord);
vec4 Sinc(sampler2D u_data, vec2 u_shape, vec2 v_texcoord);
vec4 Lanczos(sampler2D u_data, vec2 u_shape, vec2 v_texcoord);
vec4 Blackman(sampler2D u_data, vec2 u_shape, vec2 v_texcoord);

void main()
{
    vec2 P = gl_PointCoord.xy - vec2(0.5,0.5);
    P = vec2(v_rotation.x*P.x - v_rotation.y*P.y,
             v_rotation.y*P.x + v_rotation.x*P.y);
    P += vec2(0.5,0.5);

    float r = v_size + 2*(v_linewidth + 1.5*v_antialias);
    // float signed_distance = r * (texture2D(u_texture, P).r - 0.5);
    float signed_distance = r * (Bicubic(u_texture, u_texture_shape, P).r - 0.5);
    float t = v_linewidth/2.0 - v_antialias;
    float border_distance = abs(signed_distance) - t;
    float alpha = border_distance/v_antialias;
    alpha = exp(-alpha*alpha);


    // Within linestroke
    if( border_distance < 0 )
        gl_FragColor = v_fg_color;
    else if( signed_distance < 0 )
        // Inside shape
        if( border_distance > (v_linewidth/2.0 + v_antialias) )
            gl_FragColor = v_bg_color;
        else // Line stroke interior border
            gl_FragColor = mix(v_bg_color,v_fg_color,alpha);
    else
        // Outide shape
        if( border_distance > (v_linewidth/2.0 + v_antialias) )
            discard;
        else // Line stroke exterior border
            gl_FragColor = vec4(v_fg_color.rgb, v_fg_color.a * alpha);
}
