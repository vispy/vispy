// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#include "colormaps/util.glsl"

vec3 colormap_winter(float t)
{
    return mix(vec3(0.0,0.0,1.0), vec3(0.0,1.0,0.5), sqrt(t));
}

vec3 colormap_winter(float t, vec3 under, vec3 over)
{
    return colormap_underover(t, colormap_winter(t), under, over);
}

vec4 colormap_winter(float t, vec4 under, vec4 over)
{
    return colormap_underover(t, vec4(colormap_winter(t),1.0), under, over);
}
