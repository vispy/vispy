// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#include "colormaps/util.glsl"

vec3 colormap_gray(float t)
{
    return vec3(t);
}

vec3 colormap_gray(float t, vec3 under, vec3 over)
{
    return colormap_underover(t, colormap_gray(t), under, over);
}

vec4 colormap_gray(float t, vec4 under, vec4 over)
{
    return colormap_underover(t, vec4(colormap_gray(t),1.0), under, over);
}
