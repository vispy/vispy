# Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
# Distributed under the (new) BSD License.

"""Antialiasing GLSL functions."""


# -----------------------------------------------------------------------------
# Stroke
# -----------------------------------------------------------------------------

"""Compute antialiased fragment color for a stroke line.

Inputs:

- distance (float): Signed distance to border (in pixels).


Template variables:

- linewidth (float): Stroke line width (in pixels).
- antialias (float): Stroke antialiased area (in pixels).
- stroke (vec4): Stroke color.


Outputs:

- color (vec4): The final color.

"""
ANTIALIAS_STROKE = """
vec4 stroke(float distance)
{
    vec4 frag_color;
    float t = $linewidth/2.0 - $antialias;
    float signed_distance = distance;
    float border_distance = abs(signed_distance) - t;
    float alpha = border_distance/$antialias;
    alpha = exp(-alpha*alpha);

    if( border_distance < 0.0 )
        frag_color = $stroke;
    else
        frag_color = vec4($stroke.rgb, $stroke.a * alpha);

    return frag_color;
}
"""


# -----------------------------------------------------------------------------
# Stroke
# -----------------------------------------------------------------------------

"""Compute antialiased fragment color for an outlined shape.

Inputs:

- distance (float): Signed distance to border (in pixels).

Template variables:

- linewidth (float): Stroke line width (in pixels).
- antialias (float): Stroke antialiased area (in pixels).
- stroke (vec4): Stroke color.
- fill (vec4): Fill color.

Outputs:

- color (vec4): The final color.

"""
ANTIALIAS_OUTLINE = """
vec4 outline(float distance)
{
    vec4 frag_color;
    float t = $linewidth/2.0 - $antialias;
    float signed_distance = distance;
    float border_distance = abs(signed_distance) - t;
    float alpha = border_distance/$antialias;
    alpha = exp(-alpha*alpha);

    if( border_distance < 0.0 )
        frag_color = $stroke;
    else if( signed_distance < 0.0 )
        frag_color = mix($fill, $stroke, sqrt(alpha));
    else
        frag_color = vec4($stroke.rgb, $stroke.a * alpha);
    return frag_color;
}
"""


# -----------------------------------------------------------------------------
# Filled
# -----------------------------------------------------------------------------

"""Compute antialiased fragment color for a filled shape.

Inputs:

- distance (float): Signed distance to border (in pixels).

Template variables:

- linewidth (float): Stroke line width (in pixels).
- antialias (float): Stroke antialiased area (in pixels).
- fill (vec4): Fill color.

Outputs:

- color (vec4): The final color.

"""
ANTIALIAS_FILLED = """
vec4 filled(float distance)
{
    vec4 frag_color;
    float t = $linewidth/2.0 - $antialias;
    float signed_distance = distance;
    float border_distance = abs(signed_distance) - t;
    float alpha = border_distance/$antialias;
    alpha = exp(-alpha*alpha);

    if( border_distance < 0.0 )
        frag_color = $fill;
    else if( signed_distance < 0.0 )
        frag_color = $fill;
    else
        frag_color = vec4($fill.rgb, alpha * $fill.a);

    return frag_color;
}
"""
