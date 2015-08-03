/**
 * Copyright (c) Vispy Development Team
 * Distributed under the (new) BSD License. See LICENSE.txt for more info.
 *
 * This file contains code for filling a shape with anti-alias.
 */

/**
 * Compute antialiased fragment color for a filled shape.
 *
 * Parameters:
 * -----------
 *
 * distance
 *     Signed distance to border (in pixels)
 * linewidth
 *     Stroke line width (in pixels)
 * antialias
 *     Stroke antialiased area (in pixels)
 * bg_color
 *     Fill color
 *
 * Return:
 * -------
 * Fragment color (vec4)
 */
vec4 filled(float distance, float linewidth, float antialias, vec4 bg_color)
{
    vec4 frag_color;
    float t = linewidth/2.0 - antialias;
    float signed_distance = distance;
    float border_distance = abs(signed_distance) - t;
    float alpha = border_distance/antialias;
    alpha = exp(-alpha*alpha);

    if( border_distance < 0.0 ) {
        frag_color = bg_color;
    } else if( signed_distance < 0.0 ) {
        frag_color = bg_color;
    } else {
        frag_color = vec4(bg_color.rgb, alpha * bg_color.a);
    }

    return frag_color;
}

vec4 filled(float distance, float linewidth, float antialias, vec4 fg_color, vec4 bg_color)
{
    return filled(distance, linewidth, antialias, fg_color);
}
