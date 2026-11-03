// ----------------------------------------------------------------------------
// Copyright (c) Vispy Development Team. All Rights Reserved.
// Distributed under the (new) BSD License. See LICENSE.txt for more info.
// ----------------------------------------------------------------------------

// Comparisons against constants like 0.0 can be folded away by compilers that
// assume no NaN (e.g. Apple's GL-on-Metal). gl_DepthRange.far is a built-in
// uniform whose value the compiler cannot see; GL clamps it to [0, 1]. Since
// it is non-negative, this test is false for every number. The two-sided test
// against an unknown uniform is not folded by the tested compilers (Apple
// GL-on-Metal). isnan() is absent in GLSL 1.20 / ES 1.0 and unreliable under
// fast math.

#ifndef _IS_NAN_
#define _IS_NAN_

bool is_nan(float x)
{
    return !(x <= gl_DepthRange.far || -gl_DepthRange.far <= x);
}

#endif
