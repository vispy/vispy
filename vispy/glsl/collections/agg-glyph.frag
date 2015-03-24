// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------

// Uniforms
// ------------------------------------
uniform sampler2D atlas_data;
uniform vec2      atlas_shape;

// Varyings
// ------------------------------------
varying vec4  v_color;
varying float v_offset;
varying vec2  v_texcoord;


// Main
// ------------------------------------
void main(void)
{
    <viewport.clipping>;

    vec2 viewport = <viewport.viewport_global>.zw;

    vec4 current = texture2D(atlas_data, v_texcoord);
    vec4 previous= texture2D(atlas_data, v_texcoord+vec2(-1.0,0.0)/viewport);
    vec4 next    = texture2D(atlas_data, v_texcoord+vec2(+1.0,0.0)/viewport);

    float r = current.r;
    float g = current.g;
    float b = current.b;

    if( v_offset < 1.0 )
    {
        float z = v_offset;
        r = mix(current.r, previous.b, z);
        g = mix(current.g, current.r,  z);
        b = mix(current.b, current.g,  z);
    }
    else if( v_offset < 2.0 )
    {
        float z = v_offset - 1.0;
        r = mix(previous.b, previous.g, z);
        g = mix(current.r,  previous.b, z);
        b = mix(current.g,  current.r,  z);
    }
   else //if( v_offset <= 1.0 )
    {
        float z = v_offset - 2.0;
        r = mix(previous.g, previous.r, z);
        g = mix(previous.b, previous.g, z);
        b = mix(current.r,  previous.b, z);
    }

   float t = max(max(r,g),b);
   vec4 color = vec4(v_color.rgb, (r+g+b)/3.0);
   color = t*color + (1.0-t)*vec4(r,g,b, min(min(r,g),b));
   gl_FragColor = vec4( color.rgb, v_color.a*color.a);
}
