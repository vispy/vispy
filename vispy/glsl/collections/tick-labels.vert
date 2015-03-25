// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#include "math/constants.glsl"
#include "misc/viewport-NDC.glsl"

// Externs
// ------------------------------------
// vec2 position;
// vec2 texcoord;
// float scale;
// vec3 origin;
// vec3 direction
// vec4 color;

// Varyings
// ------------------------------------
varying float v_scale;
varying vec2  v_texcoord;
varying vec4  v_color;


// This works because we know the matplotlib API and how a transform is built
float xscale(float x)        { return <transform.xscale.forward!(x)>; }
float yscale(float y)        { return <transform.yscale.forward!(y)>; }
float zscale(float z)        { return <transform.zscale.forward!(z)>; }
vec3 data_projection(vec3 P) { return <transform.data_projection.forward!(P)>.xyz; }
vec4 view_projection(vec3 P) { return <transform.view_projection.transform!(vec4(P,1))>; }

vec3 data_scale(vec3 P)      { return vec3(xscale(P.x), yscale(P.y), zscale(P.z)); }
vec4 transform(vec3 P)       { return view_projection(data_projection(data_scale(P))); }


// Main
// ------------------------------------
void main()
{
    fetch_uniforms();

    vec3 up = vec3(0,0,-1);

    vec3 O = data_projection(data_scale(origin));

    vec3 tangent = normalize(data_projection(data_scale(origin+scale*direction)) - O);
    vec3 ortho = normalize(cross(tangent, up));

    vec3 P1 = O + scale*(position.x*tangent + position.y*ortho);
    vec4 P1_ = view_projection(P1);
    vec2 p1 = NDC_to_viewport(P1_, <viewport.viewport_global>.zw);

    // This compute an estimation of the actual size of the glyph
    vec3 P2 = O + scale*(tangent*(position.x+64.0) + ortho*(position.y));
    vec4 P2_ = view_projection(P2);
    vec2 p2 = NDC_to_viewport(P2_, <viewport.viewport_global>.zw);

    vec3 P3 = O + scale*(tangent*(position.x) + ortho*(position.y+64.0));
    vec4 P3_ = view_projection(P3);
    vec2 p3 = NDC_to_viewport(P3_, <viewport.viewport_global>.zw);

    float d2 = length(p2 - p1);
    float d3 = length(p3 - p1);
    v_scale = min(d2,d3);


    gl_Position = P1_;
    v_texcoord = texcoord;
    v_color = color;

    <viewport.transform>;
}
