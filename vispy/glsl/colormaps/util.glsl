// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------

/*
 * t <= 0    : return 0
 * 0 < t < 1 : return t
 * t >= 1    : return 0
 */
float
colormap_segment(float edge0, float edge1, float x)
{
    return step(edge0,x) * (1.0-step(edge1,x));
}

/*
 * t <= 0    : return under
 * 0 < t < 1 : return color
 * t >= 1    : return over
 */
vec3
colormap_underover(float t, vec3 color, vec3 under, vec3 over)
{
    return step(t,0.0)*under +
           colormap_segment(0.0,1.0,t)*color +
           step(1.0,t)*over;
}

/*
 * t <= 0    : return under
 * 0 < t < 1 : return color
 * t >= 1    : return over
 */
vec4
colormap_underover(float t, vec4 color, vec4 under, vec4 over)
{
    return step(t,0.0)*under +
           colormap_segment(0.0,1.0,t)*color +
           step(1.0,t)*over;
}
