// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#include "colormaps/util.glsl"

uniform sampler1D colormap;

vec3 colormap_user(float t)
{
    return texture1D(colormap, t).rgb;
}

vec3 colormap_user(float t, vec3 under, vec3 over)
{
    return colormap_underover(t, colormap_user(t), under, over);
}

vec4 colormap_user(float t, vec4 under, vec4 over)
{
    return colormap_underover(t, vec4(colormap_user(t),1.0), under, over);
}
