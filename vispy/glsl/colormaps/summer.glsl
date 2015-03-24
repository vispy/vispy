// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#include "colormaps/util.glsl"

vec3 colormap_summer(float t)
{
    return mix(vec3(0.0,0.5,0.4), vec3(1.0,1.0,0.4), t);
}

vec3 colormap_summer(float t, vec3 under, vec3 over)
{
    return colormap_underover(t, colormap_summer(t), under, over);
}

vec4 colormap_summer(float t, vec4 under, vec4 over)
{
    return colormap_underover(t, vec4(colormap_summer(t),1.0), under, over);
}
