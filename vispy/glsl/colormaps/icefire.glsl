// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#include "colormaps/util.glsl"
#include "colormaps/ice.glsl"
#include "colormaps/fire.glsl"

vec3 colormap_icefire(float t)
{
    return colormap_segment(0.0,0.5,t) * colormap_ice(2.0*(t-0.0)) +
           colormap_segment(0.5,1.0,t) * colormap_fire(2.0*(t-0.5));
}

vec3 colormap_icefire(float t, vec3 under, vec3 over)
{
    return colormap_underover(t, colormap_icefire(t), under, over);
}

vec4 colormap_icefire(float t, vec4 under, vec4 over)
{
    return colormap_underover(t, vec4(colormap_icefire(t),1.0), under, over);
}
