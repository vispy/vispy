// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------

// Constants
// ------------------------------------
const float M_PI = 3.14159265358979323846;
const float M_SQRT2 = 1.41421356237309504880;


// Uniforms
// ------------------------------------

// Line antialias area (usually 1 pixel)
uniform float u_antialias;

// Cartesian limits
uniform vec4 u_limits1;

// Projected limits
uniform vec4 u_limits2;

// Major grid steps
uniform vec2 u_major_grid_step;

// Minor grid steps
uniform vec2 u_minor_grid_step;

// Major grid line width (1.50 pixel)
uniform float u_major_grid_width;

// Minor grid line width (0.75 pixel)
uniform float u_minor_grid_width;

// Major grid line color
uniform vec4 u_major_grid_color;

// Minor grid line color
uniform vec4 u_minor_grid_color;


// Varyings
// ------------------------------------

// Texture coordinates (from (-0.5,-0.5) to (+0.5,+0.5)
varying vec2 v_texcoord;

// Quad size (pixels)
varying vec2 v_size;



// Functions
// ------------------------------------

// Hammer forward transform
// ------------------------------------
vec2 transform_forward(vec2 P)
{
    const float B = 2.0;
    float longitude = P.x;
    float latitude  = P.y;
    float cos_lat = cos(latitude);
    float sin_lat = sin(latitude);
    float cos_lon = cos(longitude/B);
    float sin_lon = sin(longitude/B);
    float d = sqrt(1.0 + cos_lat * cos_lon);
    float x = (B * M_SQRT2 * cos_lat * sin_lon) / d;
    float y =     (M_SQRT2 * sin_lat) / d;
    return vec2(x,y);
}

// Hammer inverse transform
// ------------------------------------
vec2 transform_inverse(vec2 P)
{
    const float B = 2.0;
    float x = P.x;
    float y = P.y;
    float z = 1.0 - (x*x/16.0) - (y*y/4.0);
    if (z < 0.0) discard;
    z = sqrt(z);
    float lon = 2.0*atan( (z*x),(2.0*(2.0*z*z - 1.0)));
    float lat = asin(z*y);
    return vec2(lon,lat);
}

/*
// Forward transform (polar)
// ------------------------------------
vec2 transform_forward(vec2 P)
{
    float x = P.x * cos(P.y);
    float y = P.x * sin(P.y);
    return vec2(x,y);
}

// Inverse transform (polar)
// ------------------------------------
vec2 transform_inverse(vec2 P)
{
    float rho = length(P);
    float theta = atan(P.y,P.x);
    if( theta < 0.0 )
        theta = 2.0*M_PI+theta;
    return vec2(rho,theta);
}
*/

// [-0.5,-0.5]x[0.5,0.5] -> [xmin,xmax]x[ymin,ymax]
// ------------------------------------------------
vec2 scale_forward(vec2 P, vec4 limits)
{
    // limits = xmin,xmax,ymin,ymax
    P += vec2(.5,.5);
    P *= vec2(limits[1] - limits[0], limits[3]-limits[2]);
    P += vec2(limits[0], limits[2]);
    return P;
}

// [xmin,xmax]x[ymin,ymax] -> [-0.5,-0.5]x[0.5,0.5]
// ------------------------------------------------
vec2 scale_inverse(vec2 P, vec4 limits)
{
    // limits = xmin,xmax,ymin,ymax
    P -= vec2(limits[0], limits[2]);
    P /= vec2(limits[1]-limits[0], limits[3]-limits[2]);
    return P - vec2(.5,.5);
}

// Antialias stroke alpha coeff
float stroke_alpha(float distance, float linewidth, float antialias)
{
    float t = linewidth/2.0 - antialias;
    float signed_distance = distance;
    float border_distance = abs(signed_distance) - t;
    float alpha = border_distance/antialias;
    alpha = exp(-alpha*alpha);

    if( border_distance > (linewidth/2.0 + antialias) )
        return 0.0;
    else if( border_distance < 0.0 )
        return 1.0;
    else
        return alpha;
}

// Compute the nearest tick from a (normalized) t value
float get_tick(float t, float vmin, float vmax, float step)
{
    float first_tick = floor((vmin + step/2.0)/step) * step;
    float last_tick = floor((vmax - step/2.0)/step) * step;
    float tick = vmin + t*(vmax-vmin);
    if (tick < (vmin + (first_tick-vmin)/2.0))
        return vmin;
    if (tick > (last_tick + (vmax-last_tick)/2.0))
        return vmax;
    tick += step/2.0;
    tick = floor(tick/step)*step;
    return min(max(vmin,tick),vmax);
}


void main()
{
    vec2 NP1 = v_texcoord;
    vec2 P1 = scale_forward(NP1, u_limits1);
    vec2 P2 = transform_inverse(P1);

    // Test if we are within limits but we do not discard yet because we want
    // to draw border. Discarding would mean half of the exterior not drawn.
    bvec2 outside = bvec2(false);
    if( P2.x < u_limits2[0] ) outside.x = true;
    if( P2.x > u_limits2[1] ) outside.x = true;
    if( P2.y < u_limits2[2] ) outside.y = true;
    if( P2.y > u_limits2[3] ) outside.y = true;

    vec2 NP2 = scale_inverse(P2,u_limits2);
    vec2 P;
    float tick;

    tick = get_tick(NP2.x+.5, u_limits2[0], u_limits2[1], u_major_grid_step[0]);
    P = transform_forward(vec2(tick,P2.y));
    P = scale_inverse(P, u_limits1);
    float Mx = length(v_size * (NP1 - P));

    tick = get_tick(NP2.x+.5, u_limits2[0], u_limits2[1], u_minor_grid_step[0]);
    P = transform_forward(vec2(tick,P2.y));
    P = scale_inverse(P, u_limits1);
    float mx = length(v_size * (NP1 - P));

    tick = get_tick(NP2.y+.5, u_limits2[2], u_limits2[3], u_major_grid_step[1]);
    P = transform_forward(vec2(P2.x,tick));
    P = scale_inverse(P, u_limits1);
    float My = length(v_size * (NP1 - P));

    tick = get_tick(NP2.y+.5, u_limits2[2], u_limits2[3], u_minor_grid_step[1]);
    P = transform_forward(vec2(P2.x,tick));
    P = scale_inverse(P, u_limits1);
    float my = length(v_size * (NP1 - P));

    float M = min(Mx,My);
    float m = min(mx,my);

    // Here we take care of "finishing" the border lines
    if( outside.x && outside.y ) {
        if (Mx > 0.5*(u_major_grid_width + u_antialias)) {
            discard;
        } else if (My > 0.5*(u_major_grid_width + u_antialias)) {
            discard;
        } else {
            M = max(Mx,My);
        }
    } else if( outside.x ) {
        if (Mx > 0.5*(u_major_grid_width + u_antialias)) {
            discard;
        } else {
            M = m = Mx;
        }
    } else if( outside.y ) {
        if (My > 0.5*(u_major_grid_width + u_antialias)) {
            discard;
        } else {
            M = m = My;
        }
    }

    // Mix major/minor colors to get dominant color
    vec4 color = u_major_grid_color;
    float alpha1 = stroke_alpha( M, u_major_grid_width, u_antialias);
    float alpha2 = stroke_alpha( m, u_minor_grid_width, u_antialias);
    float alpha  = alpha1;
    if( alpha2 > alpha1*1.5 )
    {
        alpha = alpha2;
        color = u_minor_grid_color;
    }

    // For the same price you could project a texture
    // vec4 texcolor = texture2D(u_texture, vec2(NP2.x, 1.0-NP2.y));
    // gl_FragColor = mix(texcolor, color, alpha);
    gl_FragColor = vec4(color.rgb, color.a*alpha);
}
