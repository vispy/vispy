// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#include "colormaps/util.glsl"

vec3 colormap_fire(float t)
{
    return mix(mix(vec3(1,1,1), vec3(1,1,0), t),
               mix(vec3(1,1,0), vec3(1,0,0), t*t), t);
}

vec3 colormap_fire(float t, vec3 under, vec3 over)
{
    return colormap_underover(t, colormap_fire(t), under, over);
}

vec4 colormap_fire(float t, vec4 under, vec4 over)
{
    return colormap_underover(t, vec4(colormap_fire(t),1.0), under, over);
}
