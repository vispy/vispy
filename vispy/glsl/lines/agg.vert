const float THETA = 15.0 * 3.14159265358979323846264/180.0;

// Cross product of v1 and v2
float cross(in vec2 v1, in vec2 v2) {
    return v1.x*v2.y - v1.y*v2.x;
}

// Returns distance of v3 to line v1-v2
float signed_distance(in vec2 v1, in vec2 v2, in vec2 v3) {
    return cross(v2-v1,v1-v3) / length(v2-v1);
}

// Rotate v around origin
void rotate( in vec2 v, in float alpha, out vec2 result ) {
    float c = cos(alpha);
    float s = sin(alpha);
    result = vec2( c*v.x - s*v.y,
                   s*v.x + c*v.y );
}

vec2 transform_vector(vec2 x, vec2 base) {
    vec4 o = $transform(vec4(base, 0, 1));
    return ($transform(vec4(base+x, 0, 1)) - o).xy;
}


// Uniforms
//uniform mat4 u_matrix;
//uniform mat4 u_view;

attribute vec4 color;
// uniform vec2 u_scale;
// uniform vec2 tr_scale;
uniform float linewidth;
uniform float antialias;
uniform vec2 linecaps;
uniform float linejoin;
uniform float miter_limit;
attribute float alength;
uniform float dash_phase;
uniform float dash_period;
uniform float dash_index;
uniform vec2 dash_caps;
uniform float closed;


// Attributes
attribute vec2 a_position; // position of each vertex
attribute vec4 a_tangents; // vector pointing from one vertex to the next
attribute vec2 a_segment;  // distance along path
attribute vec2 a_angles;
attribute vec2 a_texcoord;

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
    v_color = color;

    v_linewidth = linewidth;
    v_antialias = antialias;
    v_linecaps  = linecaps;

    v_linejoin    = linejoin;
    v_miter_limit = miter_limit;
    v_length      = alength;
    v_dash_phase  = dash_phase;

    v_dash_period = dash_period;
    v_dash_index  = dash_index;
    v_dash_caps   = dash_caps;

    v_closed = closed;
    bool closed = (v_closed > 0.0);

    // Attributes to varyings
    v_angles  = a_angles;
    //v_segment = a_segment * u_scale.x * tr_scale.x;  // TODO: proper scaling
    //v_length  = v_length * u_scale * tr_scale;  // TODO: proper scaling
    v_segment = a_segment;

    // Thickness below 1 pixel are represented using a 1 pixel thickness
    // and a modified alpha
    v_color.a = min(v_linewidth, v_color.a);
    v_linewidth = max(v_linewidth, 1.0);

    // If color is fully transparent we just will discard the fragment anyway
    if( v_color.a <= 0.0 )
    {
        gl_Position = vec4(0.0,0.0,0.0,1.0);
        return;
    }

    // This is the actual half width of the line
    // TODO: take care of logical - physical pixel difference here.
    float w = ceil(1.25*v_antialias+v_linewidth)/2.0;

    //vec2 position = $transform(vec4(a_position,0.,1.)).xy*u_scale;
    vec2 position = $transform(vec4(a_position,0.,1.)).xy;
    // At this point, position must be in _doc_ coordinates because the line
    // width will be added to it.

    //vec2 t1 = normalize(tr_scale*a_tangents.xy);
    //vec2 t2 = normalize(tr_scale*a_tangents.zw);
    vec2 t1 = normalize(transform_vector(a_tangents.xy, a_position));
    vec2 t2 = normalize(transform_vector(a_tangents.zw, a_position));
    float u = a_texcoord.x;
    float v = a_texcoord.y;
    vec2 o1 = vec2( +t1.y, -t1.x);
    vec2 o2 = vec2( +t2.y, -t2.x);


    // This is a join
    // ----------------------------------------------------------------
    if( t1 != t2 ) {
        float angle  = atan (t1.x*t2.y-t1.y*t2.x, t1.x*t2.x+t1.y*t2.y);
        vec2 t  = normalize(t1+t2);
        vec2 o  = vec2( + t.y, - t.x);

        if ( v_dash_index > 0.0 )
        {
            // Broken angle
            // ----------------------------------------------------------------
            if( (abs(angle) > THETA) ) {
                position += v * w * o / cos(angle/2.0);
                float s = sign(angle);
                if( angle < 0.0 ) {
                    if( u == +1.0 ) {
                        u = v_segment.y + v * w * tan(angle/2.0);
                        if( v == 1.0 ) {
                            position -= 2.0 * w * t1 / sin(angle);
                            u -= 2.0 * w / sin(angle);
                        }
                    } else {
                        u = v_segment.x - v * w * tan(angle/2.0);
                        if( v == 1.0 ) {
                            position += 2.0 * w * t2 / sin(angle);
                            u += 2.0*w / sin(angle);
                        }
                    }
                } else {
                    if( u == +1.0 ) {
                        u = v_segment.y + v * w * tan(angle/2.0);
                        if( v == -1.0 ) {
                            position += 2.0 * w * t1 / sin(angle);
                            u += 2.0 * w / sin(angle);
                        }
                    } else {
                        u = v_segment.x - v * w * tan(angle/2.0);
                        if( v == -1.0 ) {
                            position -= 2.0 * w * t2 / sin(angle);
                            u -= 2.0*w / sin(angle);
                        }
                    }
                }
                // Continuous angle
                // ------------------------------------------------------------
            } else {
                position += v * w * o / cos(angle/2.0);
                if( u == +1.0 ) u = v_segment.y;
                else            u = v_segment.x;
            }
        }

        // Solid line
        // --------------------------------------------------------------------
        else
        {
            position.xy += v * w * o / cos(angle/2.0);
            if( angle < 0.0 ) {
                if( u == +1.0 ) {
                    u = v_segment.y + v * w * tan(angle/2.0);
                } else {
                    u = v_segment.x - v * w * tan(angle/2.0);
                }
            } else {
                if( u == +1.0 ) {
                    u = v_segment.y + v * w * tan(angle/2.0);
                } else {
                    u = v_segment.x - v * w * tan(angle/2.0);
                }
            }
        }

    // This is a line start or end (t1 == t2)
    // ------------------------------------------------------------------------
    } else {
        position += v * w * o1;
        if( u == -1.0 ) {
            u = v_segment.x - w;
            position -=  w * t1;
        } else {
            u = v_segment.y + w;
            position +=  w * t2;
        }
    }

    // Miter distance
    // ------------------------------------------------------------------------
    vec2 t;
    //vec2 curr = $transform(vec4(a_position,0.,1.)).xy*u_scale;
    vec2 curr = $transform(vec4(a_position,0.,1.)).xy;
    if( a_texcoord.x < 0.0 ) {
        vec2 next = curr + t2*(v_segment.y-v_segment.x);

        rotate( t1, +a_angles.x/2.0, t);
        v_miter.x = signed_distance(curr, curr+t, position);

        rotate( t2, +a_angles.y/2.0, t);
        v_miter.y = signed_distance(next, next+t, position);
    } else {
        vec2 prev = curr - t1*(v_segment.y-v_segment.x);

        rotate( t1, -a_angles.x/2.0,t);
        v_miter.x = signed_distance(prev, prev+t, position);

        rotate( t2, -a_angles.y/2.0,t);
        v_miter.y = signed_distance(curr, curr+t, position);
    }

    if (!closed && v_segment.x <= 0.0) {
        v_miter.x = 1e10;
    }
    if (!closed && v_segment.y >= v_length)
    {
        v_miter.y = 1e10;
    }

    v_texcoord = vec2( u, v*w );
    gl_Position = $px_ndc_transform($doc_px_transform(vec4(position,
                                                           0.0, 1.0)));
}
