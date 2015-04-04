// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
// Hooks:
//  <transform> : vec4 function(position, ...)
//
// ----------------------------------------------------------------------------
#include "misc/viewport-NDC.glsl"
#include "math/point-to-line-distance.glsl"
#include "math/point-to-line-projection.glsl"

// Externs
// ------------------------------------
// extern vec3  p0;
// extern vec3  p1;
// extern vec3  p2;
// extern vec3  p3;
// extern vec2  uv;
// extern vec2  caps;
// extern vec4  color;
// extern float antialias;
// extern float linewidth;
// extern float miter_limit;
// extern vec4 viewport;
// vec4 transform(vec3 position);


// Varyings
// ------------------------------------
varying vec2  v_caps;
varying vec4  v_color;

varying float v_antialias;
varying float v_linewidth;

varying float v_length;
varying vec2  v_texcoord;
varying float v_miter_limit;
varying vec2  v_bevel_distance;


// Main
// ------------------------------------
void main (void)
{
    // This function is externally generated
    fetch_uniforms();

    v_color = color;
    v_caps = caps;
    v_linewidth = linewidth;
    v_antialias = antialias;
    v_miter_limit = miter_limit;

    // transform prev/curr/next
    vec4 p0_ = $transform(vec4(p0, 1));
    vec4 p1_ = $transform(vec4(p1, 1));
    vec4 p2_ = $transform(vec4(p2, 1));
    vec4 p3_ = $transform(vec4(p3, 1));

    // prev/curr/next in viewport coordinates
    vec2 _p0 = NDC_to_viewport(p0_, viewport.zw);
    vec2 _p1 = NDC_to_viewport(p1_, viewport.zw);
    vec2 _p2 = NDC_to_viewport(p2_, viewport.zw);
    vec2 _p3 = NDC_to_viewport(p3_, viewport.zw);

    v_antialias = antialias;
    v_linewidth = linewidth;
    v_miter_limit = miter_limit;

    // Determine the direction of each of the 3 segments (previous, current, next)
    vec2 v0 = normalize(_p1 - _p0);
    vec2 v1 = normalize(_p2 - _p1);
    vec2 v2 = normalize(_p3 - _p2);


    // Determine the normal of each of the 3 segments (previous, current, next)
    vec2 n0 = vec2(-v0.y, v0.x);
    vec2 n1 = vec2(-v1.y, v1.x);
    vec2 n2 = vec2(-v2.y, v2.x);

    // Determine miter lines by averaging the normals of the 2 segments
    vec2 miter_a;
    vec2 miter_b;
    const float epsilon = 0.1;

    // WARN: Here we test if v0 = -v1 relatively to epsilon
    if( length(v0+v1) < epsilon ) {
        miter_a = n1;
    } else {
        miter_a = normalize(n0 + n1); // miter at start of current segment
    }

    // WARN: Here we test if v1 = -v2 relatively to epsilon
    if( length(v1+v2) < epsilon ) {
        miter_b = n1;
    } else {
        miter_b = normalize(n1 + n2); // miter at end of current segment
    }

    // Determine the length of the miter by projecting it onto normal
    vec2 p,v;
    float d, z;
    float w = linewidth/2.0 + 1.5*antialias;
    v_length = length(_p2-_p1);
    float m = miter_limit*linewidth/2.0;
    float length_a = w / dot(miter_a, n1);
    float length_b = w / dot(miter_b, n1);


    // Angle between prev and current segment (sign only)
    float d0 = +1.0;
    if( (v0.x*v1.y - v0.y*v1.x) > 0. ) { d0 = -1.0;}

    // Angle between current and next segment (sign only)
    float d1 = +1.0;
    if( (v1.x*v2.y - v1.y*v2.x) > 0. ) { d1 = -1.0; }

    // Adjust vertex position
    if (uv.x == -1.) {
        z = p1_.z / p1_.w;

        // Cap at start
        if( p0 == p1 ) {
            p = _p1 - w*v1 + uv.y* w*n1;
            v_texcoord = vec2(-w, uv.y*w);
            v_caps.x = v_texcoord.x;
            // Regular join
        } else {
            p = _p1 + uv.y * length_a * miter_a;
            v_texcoord = vec2(point_to_line_projection(_p1,_p2,p), uv.y*w);
            v_caps.x = 1.0;
        }
        if( p2 == p3 ) {
            v_caps.y = v_texcoord.x;
        } else {
            v_caps.y = 1.0;
        }
        v_bevel_distance.x = uv.y*d0*point_to_line_distance(_p1+d0*n0*w, _p1+d0*n1*w, p);
        v_bevel_distance.y =        -point_to_line_distance(_p2+d1*n1*w, _p2+d1*n2*w, p);
    } else {
        z = p2_.z / p2_.w;

        // Cap at end
        if( p2 == p3 ) {
            p = _p2 + w*v1 + uv.y*w*n1;
            v_texcoord = vec2(v_length+w, uv.y*w);
            v_caps.y = v_texcoord.x;
        // Regular join
        } else {
            p = _p2 + uv.y*length_b * miter_b;
            v_texcoord = vec2(point_to_line_projection(_p1,_p2,p), uv.y*w);
            v_caps.y = 1.0;
        }
        if( p0 == p1 ) {
            v_caps.x = v_texcoord.x;
        } else {
            v_caps.x = 1.0;
        }
        v_bevel_distance.x =        -point_to_line_distance(_p1+d0*n0*w, _p1+d0*n1*w, p);
        v_bevel_distance.y = uv.y*d1*point_to_line_distance(_p2+d1*n1*w, _p2+d1*n2*w, p);
    }

    gl_Position = viewport_to_NDC(vec3(p,z), viewport.zw);
}
