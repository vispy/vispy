// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------

vec2 NDC_to_viewport(vec4 position, vec2 viewport)
{
    vec2 p = position.xy/position.w;
    return (p+1.0)/2.0 * viewport;
}

vec4 viewport_to_NDC(vec2 position, vec2 viewport)
{
    return vec4(2.0*(position/viewport) - 1.0, 0.0, 1.0);
}

vec4 viewport_to_NDC(vec2 position, vec2 viewport, float z)
{
    return vec4(2.0*(position/viewport) - 1.0, z, 1.0);
}
