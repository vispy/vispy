// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
// Hooks:
//  <transform> : vec4 function(position, ...)
//
// ----------------------------------------------------------------------------
#include "misc/viewport-NDC.glsl"

// Externs
// ------------------------------------
// extern vec3  prev;
// extern vec3  curr;
// extern vec3  next;
// extern float id;
// extern vec4  color;
// extern float antialias;
// extern float linewidth;
// extern vec4 viewport;
//        vec4 transform(vec3 position);

// Varyings
// ------------------------------------
varying float v_antialias;
varying float v_linewidth;
varying float v_distance;
varying vec4  v_color;


// Main
// ------------------------------------
void main (void)
{
    // This function is externally generated
    fetch_uniforms();
    v_linewidth = linewidth;
    v_antialias = antialias;
    v_color     = color;

    // transform prev/curr/next
    vec4 prev_ = $transform(vec4(prev, 1));
    vec4 curr_ = $transform(vec4(curr, 1));
    vec4 next_ = $transform(vec4(next, 1));

    // prev/curr/next in viewport coordinates
    vec2 _prev = NDC_to_viewport(prev_, viewport.zw);
    vec2 _curr = NDC_to_viewport(curr_, viewport.zw);
    vec2 _next = NDC_to_viewport(next_, viewport.zw);

    // Compute vertex final position (in viewport coordinates)
    float w = linewidth/2.0 + 1.5*antialias;
    float z;
    vec2 P;
    if( curr == prev) {
        vec2 v = normalize(_next.xy - _curr.xy);
        vec2 normal = normalize(vec2(-v.y,v.x));
        P = _curr.xy + normal*w*id;
    } else if (curr == next) {
        vec2 v = normalize(_curr.xy - _prev.xy);
        vec2 normal  = normalize(vec2(-v.y,v.x));
        P = _curr.xy + normal*w*id;
    } else {
        vec2 v0 = normalize(_curr.xy - _prev.xy);
        vec2 v1 = normalize(_next.xy - _curr.xy);
        vec2 normal  = normalize(vec2(-v0.y,v0.x));
        vec2 tangent = normalize(v0+v1);
        vec2 miter   = vec2(-tangent.y, tangent.x);
        float l = abs(w / dot(miter,normal));
        P = _curr.xy + miter*l*sign(id);
    }

    if( abs(id) > 1.5 ) v_color.a = 0.0;

    v_distance = w*id;
    gl_Position = viewport_to_NDC(vec3(P, curr_.z/curr_.w), viewport.zw);

}
