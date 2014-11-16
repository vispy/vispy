"""Color-related GLSL functions."""


# -----------------------------------------------------------------------------
# Colormaps
# -----------------------------------------------------------------------------

"""Texture lookup for a discrete color map stored in a 1*ncolors 2D texture.

The `get_color()` function returns a RGB color from an index integer
referring to the colormap.

Inputs
------
index : int
    The color index.

Outputs
-------
color : vec3
    The color.

Template variables
------------------
$ncolors : int
    The number of colors in the colormap.

$colormap : 2D texture sampler
    The sampler for the 2D 1*ncolors colormap texture.


"""
COLORMAP_DISCRETE = """
vec3 get_color(int index) {
    float x = (float(index) + .5) / float($ncolors);
    return texture2D($colormap, vec2(x, .5)).rgb;
}
"""
