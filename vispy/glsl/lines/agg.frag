#include "math/constants.glsl"

const float THETA = 15.0 * 3.14159265358979323846264/180.0;

float
cap( int type, float dx, float dy, float t )
{
    float d = 0.0;
    dx = abs(dx);
    dy = abs(dy);

    // None
    if      (type == 0)  discard;
    // Round
    else if (type == 1)  d = sqrt(dx*dx+dy*dy);
    // Triangle in
    else if (type == 3)  d = (dx+abs(dy));
    // Triangle out
    else if (type == 2)  d = max(abs(dy),(t+dx-abs(dy)));
    // Square
    else if (type == 4)  d = max(dx,dy);
    // Butt
    else if (type == 5)  d = max(dx+t,dy);

    return d;
}

float
join( in int type, in float d, in vec2 segment, in vec2 texcoord,
      in vec2 miter, in float miter_limit, in float linewidth )
{
    float dx = texcoord.x;

    // Round join
    // --------------------------------
    if( type == 1 )
    {
        if (dx < segment.x) {
            d = max(d,length( texcoord - vec2(segment.x,0.0)));
            //d = length( texcoord - vec2(segment.x,0.0));
        } else if (dx > segment.y) {
            d = max(d,length( texcoord - vec2(segment.y,0.0)));
            //d = length( texcoord - vec2(segment.y,0.0));
        }
    }

    // Bevel join
    // --------------------------------
    else if ( type == 2 )
    {
        if( (dx < segment.x) ||  (dx > segment.y) )
            d = max(d, min(abs(miter.x),abs(miter.y)));
    }

    // Miter limit
    // --------------------------------
    if( (dx < segment.x) ||  (dx > segment.y) )
    {
        d = max(d, min(abs(miter.x),
                       abs(miter.y)) - miter_limit*linewidth/2.0 );
    }

    return d;
}


// Uniforms
uniform sampler2D u_dash_atlas;

// Varying
varying vec4  v_color;
varying vec2  v_segment;
varying vec2  v_angles;
varying vec2  v_linecaps;
varying vec2  v_texcoord;
varying vec2  v_miter;
varying float v_miter_limit;
varying float v_length;
varying float v_linejoin;
varying float v_linewidth;
varying float v_antialias;
varying float v_dash_phase;
varying float v_dash_period;
varying float v_dash_index;
varying vec2  v_dash_caps;
varying float v_closed;
void main()
{
    // gl_FragColor = v_color; return;
    // vec4 color = v_color;

    // If color is fully transparent we just discard the fragment
    if( v_color.a <= 0.0 ) {
        discard;
    }

    // Test if dash pattern is the solid one (0)
    bool solid = (v_dash_index == 0.0);

    float dx = v_texcoord.x;
    float dy = v_texcoord.y;
    float t = v_linewidth/2.0-v_antialias;
    float width = v_linewidth;
    float d = 0.0;

    vec2 linecaps = v_linecaps;
    vec2 dash_caps = v_dash_caps;
    float line_start = 0.0;
    float line_stop  = v_length;
    // Test if path is closed
    bool closed = (v_closed > 0.0);

    // ------------------------------------------------------------------------
    // Solid line
    // ------------------------------------------------------------------------
    if( solid ) {
        d = abs(dy);

        if( (!closed) && (dx < line_start) )
        {
            d = cap( int(v_linecaps.x), abs(dx), abs(dy), t );
        }
        else if( (!closed) &&  (dx > line_stop) )
        {
            d = cap( int(v_linecaps.y), abs(dx)-line_stop, abs(dy), t );
        }
        else
        {
            d = join( int(v_linejoin), abs(dy), v_segment, v_texcoord,
                      v_miter, v_miter_limit, v_linewidth );
        }

    // ------------------------------------------------------------------------
    // Dash line
    // ------------------------------------------------------------------------
    } else {
        float segment_start = v_segment.x;
        float segment_stop  = v_segment.y;
        float segment_center = (segment_start+segment_stop)/2.0;
        float freq = v_dash_period*width;
        float u = mod( dx + v_dash_phase*width,freq );
        vec4 tex = texture2D(u_dash_atlas, vec2(u/freq, v_dash_index));
        float dash_center= tex.x * width;
        float dash_type  = tex.y;
        float _start = tex.z * width;
        float _stop  = tex.a * width;
        float dash_start = dx - u + _start;
        float dash_stop  = dx - u + _stop;

        // This test if the we are dealing with a discontinuous angle
        bool discont = ((dx <  segment_center) && abs(v_angles.x) > THETA) ||
                       ((dx >= segment_center) && abs(v_angles.y) > THETA);
        if( dx < line_start) discont = false;
        if( dx > line_stop)  discont = false;

        // When path is closed, we do not have room for linecaps, so we make
        // room by shortening the total length
        if (closed){
            line_start += v_linewidth/2.0;
            line_stop  -= v_linewidth/2.0;
            linecaps = v_dash_caps;
        }


        // Check is dash stop is before line start
        if( dash_stop <= line_start )
        {
            discard;
        }
        // Check is dash start is beyond line stop
        if( dash_start >= line_stop )
        {
            discard;
        }

        // Check if current pattern start is beyond segment stop
        if( discont )
        {
            // Dash start is beyond segment, we discard
            if( dash_start > segment_stop )
            {
                discard;
            }

            // Dash stop is before segment, we discard
            if( dash_stop < segment_start )
            {
                discard;
            }

            // Special case for round caps (nicer with this)
            if( (u > _stop) && (dash_stop > segment_stop ) &&
                (abs(v_angles.y) < M_PI/2.0))
            {
                if( dash_caps.x == 1.0) discard;
            }
            // Special case for round caps  (nicer with this)
            else if( (u < _start) && (dash_start < segment_start ) &&
                     (abs(v_angles.x) < M_PI/2.0))
            {
                if( dash_caps.y == 1.0) discard;
            }

            // Special case for triangle caps (in & out) and square
            // We make sure the cap stop at crossing frontier
            if( (dash_caps.x != 1.0) && (dash_caps.x != 5.0) )
            {
                if( (dash_start < segment_start ) &&
                    (abs(v_angles.x) < M_PI/2.0) )
                {
                    float a = v_angles.x/2.0;
                    float x = (segment_start-dx)*cos(a) - dy*sin(a);
                    float y = (segment_start-dx)*sin(a) + dy*cos(a);
                    if( (x > 0.0) ) discard;
                    // We transform the cap into square to avoid holes
                    dash_caps.x = 4.0;
                }
            }
            // Special case for triangle caps (in & out) and square
            // We make sure the cap stop at crossing frontier
            if( (dash_caps.y != 1.0) && (dash_caps.y != 5.0) )
            {
                if( (dash_stop > segment_stop ) &&
                    (abs(v_angles.y) < M_PI/2.0) )
                {
                    float a = v_angles.y/2.0;
                    float x = (dx-segment_stop)*cos(a) - dy*sin(a);
                    float y = (dx-segment_stop)*sin(a) + dy*cos(a);
                    if( (x > 0.0) ) discard;
                    // We transform the caps into square to avoid holes
                    dash_caps.y = 4.0;
                }
            }
        }

        // Line cap at start
        if( (dx < line_start) && (dash_start < line_start) &&
            (dash_stop > line_start) )
        {
            d = cap( int(linecaps.x), dx-line_start, dy, t);
        }
        // Line cap at stop
        else if( (dx > line_stop) && (dash_stop > line_stop) &&
                 (dash_start < line_stop)  )
        {
            d = cap( int(linecaps.y), dx-line_stop, dy, t);
        }
        // Dash cap left
        else if( dash_type < 0.0 )
        {
            float u = max( u-dash_center , 0.0 );
            d = cap( int(dash_caps.y), abs(u), dy, t);
        }
        // Dash cap right
        else if( dash_type > 0.0 )
        {
            float u = max( dash_center-u, 0.0 );
            d = cap( int(dash_caps.x), abs(u), dy, t);
        }
        // Dash body (plain)
        else if( dash_type == 0.0 )
        {
            d = abs(dy);
        }

        // Antialiasing at segment angles region
        if( discont )
        {
            if( dx < segment_start )
            {
                // For sharp angles, we do not enforce cap shape
                if( (dash_start < segment_start ) &&
                    (abs(v_angles.x) > M_PI/2.0))
                {
                    d = abs(dy);
                }
                // Antialias at outer border
                dx = segment_start - dx;
                float angle = M_PI/2.+v_angles.x;
                float f = abs( dx*cos(angle) - dy*sin(angle));
                d = max(f,d);
            }
            else if( (dx > segment_stop) )
            {
                // For sharp angles, we do not enforce cap shape
                if( (dash_stop > segment_stop ) &&
                    (abs(v_angles.y) > M_PI/2.0) )
                {
                    d = abs(dy);
                }
                // Antialias at outer border
                dx = dx - segment_stop;
                float angle = M_PI/2.+v_angles.y;
                float f = abs( dx*cos(angle) - dy*sin(angle));
                d = max(f,d);
            }
        }

        // Line join
        //if( (dx > line_start) && (dx < line_stop) )
        {
            d = join( int(v_linejoin), d, v_segment, v_texcoord,
                      v_miter, v_miter_limit, v_linewidth );
        }
    }


    // Distance to border
    // ------------------------------------------------------------------------
    d = d - t;
    if( d < 0.0 )
    {
        gl_FragColor = v_color;
    }
    else
    {
        d /= v_antialias;
        gl_FragColor = vec4(v_color.xyz, exp(-d*d)*v_color.a);
    }
}
