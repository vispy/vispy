// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#include "colormaps/util.glsl"

// Wheel colormap by Morgan McGuire
vec3 colormap_wheel(float t)
{
    return clamp(abs(fract(t + vec3(1.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0) -1.0, 0.0, 1.0);
}

vec3 colormap_wheel(float t, vec3 under, vec3 over)
{
    return colormap_underover(t, colormap_wheel(t), under, over);
}

vec4 colormap_wheel(float t, vec4 under, vec4 over)
{
    return colormap_underover(t, vec4(colormap_wheel(t),1.0), under, over);
}
