// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
uniform vec4 viewport_local;
uniform vec4 viewport_global;
uniform int viewport_transform;
uniform int viewport_clipping;

#ifdef __VERTEX_SHADER__
void transform(void)
{
    if (viewport_transform == 0) return;

    vec4 position = gl_Position;

    float w = viewport_local.z / viewport_global.z;
    float h = viewport_local.w / viewport_global.w;
    float x = 2.0*(viewport_local.x / viewport_global.z) - 1.0 + w;
    float y = 2.0*(viewport_local.y / viewport_global.w) - 1.0 + h;

    gl_Position = vec4((x + w*position.x/position.w)*position.w,
                       (y + h*position.y/position.w)*position.w,
                       position.z, position.w);
}
#endif

#ifdef __FRAGMENT_SHADER__
void clipping(void)
{
//    if (viewport_clipping == 0) return;

    vec2 position = gl_FragCoord.xy;
         if( position.x < (viewport_local.x))                  discard;
    else if( position.x > (viewport_local.x+viewport_local.z)) discard;
    else if( position.y < (viewport_local.y))                  discard;
    else if( position.y > (viewport_local.y+viewport_local.w)) discard;

    /*
    if( length(position.x - viewport_local.x) < 1.0 )
        gl_FragColor = vec4(0,0,0,1);
    else if( length(position.x - viewport_local.x - viewport_local.z) < 1.0 )
        gl_FragColor = vec4(0,0,0,1);
    else if( length(position.y - viewport_local.y) < 1.0 )
        gl_FragColor = vec4(0,0,0,1);
    else if( length(position.y - viewport_local.y - viewport_local.w) < 1.0 )
        gl_FragColor = vec4(0,0,0,1);
    */
}
#endif
