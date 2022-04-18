"""Color-related GLSL functions."""


# -----------------------------------------------------------------------------
# Colormaps
# -----------------------------------------------------------------------------

"""Texture lookup for a discrete color map stored in a 1*ncolors 2D texture.

The `get_color()` function returns a RGB color from an index integer
referring to the colormap.


Inputs:

- index (int): The color index.

Template variables:

- $ncolors (int): The number of colors in the colormap.
- $colormap (2D texture sampler): The sampler for the 2D 1*ncolors colormap texture.

Outputs:

- color (vec3): The color.

"""
COLORMAP_TEXTURE = """
vec3 get_color(int index) {
    float x = (float(index) + .5) / float($ncolors);
    return texture2D($colormap, vec2(x, .5)).rgb;
}
"""


# -----------------------------------------------------------------------------
# Color space transformations
# -----------------------------------------------------------------------------

# From http://lolengine.net/blog/2013/07/27/rgb-to-hsv-in-glsl
# TODO: unit tests
HSV_TO_RGB = """
vec3 hsv_to_rgb(vec3 c)
{
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}
"""


RGB_TO_HSV = """
vec3 rgb_to_hsv(vec3 c)
{
    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}
"""
