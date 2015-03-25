// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#include "colormaps/util.glsl"

vec3 colormap_hot(float t)
{
    return vec3(smoothstep(0.0,    1.0/3.0,t),
                smoothstep(1.0/3.0,2.0/3.0,t),
                smoothstep(2.0/3.0,1.0,    t));
}

vec3 colormap_hot(float t, vec3 under, vec3 over)
{
    return colormap_underover(t, colormap_hot(t), under, over);
}

vec4 colormap_hot(float t, vec4 under, vec4 over)
{
    return colormap_underover(t, vec4(colormap_hot(t),1.0), under, over);
}
