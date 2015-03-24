// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------

// Constants
// ---------
const float k0 = 0.75;
const float a  = 1.00;

// Helper functions
// ----------------
float cosh(float x) { return 0.5 * (exp(x)+exp(-x)); }
float sinh(float x) { return 0.5 * (exp(x)-exp(-x)); }


/* ---------------------------------------------------------
   Transverse Mercator projection
   -> http://en.wikipedia.org/wiki/Transverse_Mercator_projection


   Parameters:
   -----------

   position : 2d position in (longitude,latitiude) coordinates

   Return:
   -------
   2d position in cartesian coordinates

   --------------------------------------------------------- */

vec2 transform_forward(vec2 P)
{
    float lambda = P.x;
    float phi = P.y;
    float x = 0.5*k0*log((1.0+sin(lambda)*cos(phi)) / (1.0 - sin(lambda)*cos(phi)));
    float y = k0*a*atan(tan(phi), cos(lambda));
    return vec2(x,y);
}
