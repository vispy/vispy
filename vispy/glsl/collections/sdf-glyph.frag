// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
// Ref: http://www.java-gaming.org/index.php?topic=33612.0
//      http://www.reddit.com/
//       -> r/gamedev/comments/2879jd/just_found_out_about_signed_distance_field_text/
#include "math/constants.glsl"
#include "misc/spatial-filters.frag"

// Uniforms
// ------------------------------------
uniform sampler2D atlas_data;
uniform vec2      atlas_shape;

// Varyings
// ------------------------------------
varying float v_scale;
varying vec2 v_texcoord;
varying vec4 v_color;


float contour(in float d, in float w)
{
    return smoothstep(0.5 - w, 0.5 + w, d);
}
float sample(sampler2D texture, vec2 uv, float w)
{
    return contour(texture2D(texture, uv).r, w);
}


// Main
// ------------------------------------
void main(void)
{
    <viewport.clipping>;

    vec4 color = v_color;

    // Retrieve distance from texture
    float dist;
    if(v_scale > 50.) {
        dist = Bicubic(atlas_data, atlas_shape, v_texcoord).r;
        // Debug
        // color = vec4(0,0,1,1);
    } else {
        dist = texture2D(atlas_data, v_texcoord).r;
    }


    // fwidth helps keep outlines a constant width irrespective of scaling
    // GLSL's fwidth = abs(dFdx(uv)) + abs(dFdy(uv))
    float width = fwidth(dist);

    // Regular SDF
    float alpha = contour( dist, width );

    // Supersampled version (when scale is small)
    if (v_scale < 30.)
    {
        // Debug
        // color = vec4(1,0,0,1);

        // Supersample, 4 extra points
        // Half of 1/sqrt2; you can play with this
        float dscale = 0.5 * M_SQRT1_2;
        vec2 duv = dscale * (dFdx(v_texcoord) + dFdy(v_texcoord));
        vec4 box = vec4(v_texcoord-duv, v_texcoord+duv);
        float asum = sample(atlas_data, box.xy, width)
                   + sample(atlas_data, box.zw, width)
                   + sample(atlas_data, box.xw, width)
                   + sample(atlas_data, box.zy, width);

        // weighted average, with 4 extra points having 0.5 weight each,
        // so 1 + 0.5*4 = 3 is the divisor
        alpha = (alpha + 0.5 * asum) / 3.0;
    }
    gl_FragColor = vec4(color.rgb, alpha*color.a);
}
