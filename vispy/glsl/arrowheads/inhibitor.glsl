/**
 * Copyright (c) Vispy Development Team
 * Distributed under the (new) BSD License. See LICENSE.txt for more info.
 *
 * This files contains the code for drawing curved arrow heads.
 */

#include "arrowheads/util.glsl"


float arrow_inhibitor_round(vec2 texcoord, float size,
                            float linewidth, float antialias)
{
    vec2 c = vec2(size/2, 0.0);
    float radius = size/2;
    float radius_inner = radius - linewidth/6;

    float d1 = length(texcoord - c) - radius;
    float d2 = length(texcoord - c) - radius_inner;
    float d3 = texcoord.x - (size/2.5);

    return max(d3, max(d1, -d2));
    //return max(d1, -d2);
}
    

