// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
#include "arrows/util.glsl"

float arrow_triangle_30(vec2 texcoord,
                        float body, float head,
                        float linewidth, float antialias)
{
    return arrow_triangle(texcoord, body, head, 0.25, linewidth, antialias);
}
