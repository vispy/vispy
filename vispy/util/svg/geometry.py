# ----------------------------------------------------------------------------
#  Anti-Grain Geometry (AGG) - Version 2.5
#  A high quality rendering engine for C++
#  Copyright (C) 2002-2006 Maxim Shemanarev
#  Contact: mcseem@antigrain.com
#           mcseemagg@yahoo.com
#           http://antigrain.com
#
#  AGG is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  AGG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with AGG; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
# ----------------------------------------------------------------------------
#
# Python translation by Nicolas P. Rougier
# Copyright (C) 2013 Nicolas P. Rougier. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY NICOLAS P. ROUGIER ''AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL NICOLAS P. ROUGIER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Nicolas P. Rougier.
#
# ----------------------------------------------------------------------------
import math
import numpy as np

curve_distance_epsilon        = 1e-30
curve_collinearity_epsilon    = 1e-30
curve_angle_tolerance_epsilon = 0.01
curve_recursion_limit         = 32
m_cusp_limit                  = 0.0
m_angle_tolerance             = 10*math.pi/180.0
m_approximation_scale         = 1.0
m_distance_tolerance_square   = (0.5 / m_approximation_scale)**2
epsilon                       = 1e-10


def calc_sq_distance( x1,y1, x2,y2 ):
    dx = x2-x1
    dy = y2-y1
    return dx * dx + dy * dy



def quadratic_recursive( points, x1, y1, x2, y2, x3, y3, level = 0 ):
    if level > curve_recursion_limit:
        return

    # Calculate all the mid-points of the line segments
    # -------------------------------------------------
    x12  = (x1 + x2) / 2.
    y12  = (y1 + y2) / 2.
    x23  = (x2 + x3) / 2.
    y23  = (y2 + y3) / 2.
    x123 = (x12 + x23) / 2.
    y123 = (y12 + y23) / 2.

    dx = x3 - x1
    dy = y3 - y1
    d = math.fabs((x2-x3)*dy - (y2-y3)*dx)

    if d > curve_collinearity_epsilon:
        # Regular case
        # ------------
        if d*d <= m_distance_tolerance_square * (dx*dx + dy*dy):
            # If the curvature doesn't exceed the distance_tolerance value
            # we tend to finish subdivisions.
            if m_angle_tolerance < curve_angle_tolerance_epsilon:
                points.append( (x123,y123) )
                return

            # Angle & Cusp Condition
            da = math.fabs(math.atan2(y3 - y2, x3 - x2) - math.atan2(y2 - y1, x2 - x1))
            if da >= math.pi:
                da = 2*math.pi - da

            if da < m_angle_tolerance:
                # Finally we can stop the recursion
                points.append( (x123,y123) )
                return
    else:
        # Collinear case
        # --------------
        da = dx*dx + dy*dy
        if da == 0:
            d = calc_sq_distance(x1, y1, x2, y2)
        else:
            d = ((x2 - x1)*dx + (y2 - y1)*dy) / da
            if d > 0 and d < 1:
                # Simple collinear case, 1---2---3, we can leave just two endpoints
                return
            if(d <= 0):
                d = calc_sq_distance(x2, y2, x1, y1)
            elif d >= 1:
                d = calc_sq_distance(x2, y2, x3, y3)
            else:
               d = calc_sq_distance(x2, y2, x1 + d*dx, y1 + d*dy)

        if d < m_distance_tolerance_square:
            points.append( (x2,y2) )
            return

    # Continue subdivision
    # --------------------
    quadratic_recursive( points, x1, y1, x12, y12, x123, y123, level + 1 )
    quadratic_recursive( points, x123, y123, x23, y23, x3, y3, level + 1 )



def cubic_recursive( points, x1, y1, x2, y2, x3, y3, x4, y4, level=0):
    if level > curve_recursion_limit:
        return

    # Calculate all the mid-points of the line segments
    # -------------------------------------------------
    x12   = (x1 + x2) / 2.
    y12   = (y1 + y2) / 2.
    x23   = (x2 + x3) / 2.
    y23   = (y2 + y3) / 2.
    x34   = (x3 + x4) / 2.
    y34   = (y3 + y4) / 2.
    x123  = (x12 + x23) / 2.
    y123  = (y12 + y23) / 2.
    x234  = (x23 + x34) / 2.
    y234  = (y23 + y34) / 2.
    x1234 = (x123 + x234) / 2.
    y1234 = (y123 + y234) / 2.


    # Try to approximate the full cubic curve by a single straight line
    # -----------------------------------------------------------------
    dx = x4 - x1
    dy = y4 - y1
    d2 = math.fabs(((x2 - x4) * dy - (y2 - y4) * dx))
    d3 = math.fabs(((x3 - x4) * dy - (y3 - y4) * dx))

    s =  int((d2 > curve_collinearity_epsilon) << 1) + int(d3 > curve_collinearity_epsilon)

    if s == 0:
        # All collinear OR p1==p4
        # ----------------------
        k = dx*dx + dy*dy
        if k == 0:
            d2 = calc_sq_distance(x1, y1, x2, y2)
            d3 = calc_sq_distance(x4, y4, x3, y3)

        else:
            k   = 1. / k
            da1 = x2 - x1
            da2 = y2 - y1
            d2  = k * (da1*dx + da2*dy)
            da1 = x3 - x1
            da2 = y3 - y1
            d3  = k * (da1*dx + da2*dy)
            if d2 > 0 and d2 < 1 and d3 > 0 and d3 < 1:
                # Simple collinear case, 1---2---3---4
                # We can leave just two endpoints
                return

            if d2 <= 0:
                d2 = calc_sq_distance(x2, y2, x1, y1)
            elif d2 >= 1:
                d2 = calc_sq_distance(x2, y2, x4, y4)
            else:
                d2 = calc_sq_distance(x2, y2, x1 + d2*dx, y1 + d2*dy)

            if d3 <= 0:
                d3 = calc_sq_distance(x3, y3, x1, y1)
            elif d3 >= 1:
                d3 = calc_sq_distance(x3, y3, x4, y4)
            else:
                d3 = calc_sq_distance(x3, y3, x1 + d3*dx, y1 + d3*dy)

        if d2 > d3:
            if d2 < m_distance_tolerance_square:
                points.append( (x2, y2) )
                return
        else:
            if d3 < m_distance_tolerance_square:
                points.append( (x3, y3) )
                return

    elif s == 1:
        # p1,p2,p4 are collinear, p3 is significant
        # -----------------------------------------
        if d3 * d3 <= m_distance_tolerance_square * (dx*dx + dy*dy):
            if m_angle_tolerance < curve_angle_tolerance_epsilon:
                points.append((x23, y23) )
                return

            # Angle Condition
            # ---------------
            da1 = math.fabs(math.atan2(y4 - y3, x4 - x3) - math.atan2(y3 - y2, x3 - x2))
            if da1 >= math.pi:
                da1 = 2*math.pi - da1

            if da1 < m_angle_tolerance:
                points.extend( [(x2, y2),(x3, y3)] )
                return

            if m_cusp_limit != 0.0:
                if da1 > m_cusp_limit:
                    points.append( (x3, y3) )
                    return

    elif s == 2:
        # p1,p3,p4 are collinear, p2 is significant
        # -----------------------------------------
        if d2 * d2 <= m_distance_tolerance_square * (dx*dx + dy*dy):
            if m_angle_tolerance < curve_angle_tolerance_epsilon:
                points.append( (x23, y23) )
                return

            # Angle Condition
            # ---------------
            da1 = math.fabs(math.atan2(y3 - y2, x3 - x2) - math.atan2(y2 - y1, x2 - x1))
            if da1 >= math.pi:
                da1 = 2*math.pi - da1

            if da1 < m_angle_tolerance:
                points.extend( [(x2, y2),(x3, y3)] )
                return

            if m_cusp_limit != 0.0:
                if da1 > m_cusp_limit:
                    points.append( (x2, y2) )
                    return

    elif s == 3:
        # Regular case
        # ------------
        if (d2 + d3)*(d2 + d3) <= m_distance_tolerance_square * (dx*dx + dy*dy):
            # If the curvature doesn't exceed the distance_tolerance value
            # we tend to finish subdivisions.

            if m_angle_tolerance < curve_angle_tolerance_epsilon:
                points.append( (x23, y23) )
                return

            # Angle & Cusp Condition
            # ----------------------
            k   = math.atan2(y3 - y2, x3 - x2)
            da1 = math.fabs(k - math.atan2(y2 - y1, x2 - x1))
            da2 = math.fabs(math.atan2(y4 - y3, x4 - x3) - k)
            if da1 >= math.pi:
                da1 = 2*math.pi - da1
            if da2 >= math.pi:
                da2 = 2*math.pi - da2

            if da1 + da2 < m_angle_tolerance:
                # Finally we can stop the recursion
                # ---------------------------------
                points.append( (x23, y23) )
                return

            if m_cusp_limit != 0.0:
                if da1 > m_cusp_limit:
                    points.append( (x2, y2) )
                    return

                if da2 > m_cusp_limit:
                    points.append( (x3, y3) )
                    return

    # Continue subdivision
    # --------------------
    cubic_recursive( points, x1, y1, x12, y12, x123, y123, x1234, y1234, level + 1 )
    cubic_recursive( points, x1234, y1234, x234, y234, x34, y34, x4, y4, level + 1 )



def quadratic( p1, p2, p3 ):
    x1,y1 = p1
    x2,y2 = p2
    x3,y3 = p3
    points = []
    quadratic_recursive( points, x1,y1, x2,y2, x3,y3 )

    dx,dy = points[0][0]-x1, points[0][1]-y1
    if (dx*dx+dy*dy) > epsilon: points.insert(0, (x1,y1) )

    dx,dy = points[-1][0]-x3, points[-1][1]-y3
    if (dx*dx+dy*dy) > epsilon: points.append( (x3,y3) )

    return points



def cubic( p1, p2, p3, p4 ):
    x1,y1 = p1
    x2,y2 = p2
    x3,y3 = p3
    x4,y4 = p4
    points = []
    cubic_recursive( points, x1,y1, x2,y2, x3,y3, x4,y4 )

    dx,dy = points[0][0]-x1, points[0][1]-y1
    if (dx*dx+dy*dy) > epsilon: points.insert(0, (x1,y1) )
    dx,dy = points[-1][0]-x4, points[-1][1]-y4
    if (dx*dx+dy*dy) > epsilon: points.append( (x4,y4) )

    return points



def arc(cx, cy, rx, ry, a1, a2, ccw=False):
    scale = 1.0
    ra = (abs(rx) + abs(ry)) / 2.0
    da = math.acos(ra / (ra + 0.125 / scale)) * 2.0
    if ccw:
        while a2 < a1:
            a2 += math.pi * 2.0
    else:
        while a1 < a2:
            a1 += math.pi * 2.0
        da = -da
    a_start = a1
    a_end   = a2

    vertices =[]
    angle = a_start
    while (angle < a_end - da/4) == ccw:
        x = cx + math.cos(angle) * rx
        y = cy + math.sin(angle) * ry
        vertices.append( (x,y) )
        angle += da
    x = cx + math.cos(a_end) * rx
    y = cy + math.sin(a_end) * ry
    vertices.append( (x,y) )
    return vertices


def elliptical_arc(x0, y0, rx, ry, angle, large_arc_flag, sweep_flag, x2, y2):
    radii_ok = True
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    if rx < 0.0: rx = -rx
    if ry < 0.0: ry = -rx

    # Calculate the middle point between
    # the current and the final points
    # ------------------------
    dx2 = (x0 - x2) / 2.0
    dy2 = (y0 - y2) / 2.0

    # Calculate (x1, y1)
    # ------------------------
    x1 =  cos_a * dx2 + sin_a * dy2
    y1 = -sin_a * dx2 + cos_a * dy2

    # Check that radii are large enough
    # ------------------------
    prx,pry = rx * rx, ry * ry
    px1,py1 = x1 * x1, y1 * y1

    radii_check = px1/prx + py1/pry
    if radii_check > 1.0:
        rx = math.sqrt(radii_check) * rx
        ry = math.sqrt(radii_check) * ry
        prx = rx * rx
        pry = ry * ry
        if radii_check > 10.0:
            radii_ok = False

    # Calculate (cx1, cy1)
    # ------------------------
    if large_arc_flag == sweep_flag:
        sign = -1
    else:
        sign = +1
    sq   = (prx*pry - prx*py1 - pry*px1) / (prx*py1 + pry*px1)
    coef = sign*math.sqrt( max(sq,0) )
    cx1  = coef *  ((rx * y1) / ry)
    cy1  = coef * -((ry * x1) / rx)

    # Calculate (cx, cy) from (cx1, cy1)
    # ------------------------
    sx2 = (x0 + x2) / 2.0
    sy2 = (y0 + y2) / 2.0
    cx = sx2 + (cos_a * cx1 - sin_a * cy1)
    cy = sy2 + (sin_a * cx1 + cos_a * cy1)

    # Calculate the start_angle (angle1) and the sweep_angle (dangle)
    # ------------------------
    ux =  (x1 - cx1) / rx
    uy =  (y1 - cy1) / ry
    vx = (-x1 - cx1) / rx
    vy = (-y1 - cy1) / ry

    # Calculate the angle start
    # ------------------------
    n = math.sqrt(ux*ux + uy*uy)
    p = ux;
    if uy < 0:
        sign = -1.0
    else:
        sign = +1.0
    v = p / n
    if v < -1.0:
        v = -1.0
    if v >  1.0:
        v =  1.0
    start_angle = sign * math.acos(v)

    # Calculate the sweep angle
    # ------------------------
    n = math.sqrt((ux*ux + uy*uy) * (vx*vx + vy*vy))
    p = ux * vx + uy * vy
    if ux * vy - uy * vx < 0:
        sign = -1.0
    else:
        sign = +1.0
    v = p / n
    v = min(max(v,-1.0),+1.0)
    sweep_angle = sign * math.acos(v)
    if not sweep_flag and sweep_angle > 0:
        sweep_angle -= math.pi * 2.0
    elif sweep_flag and sweep_angle < 0:
        sweep_angle += math.pi * 2.0

    start_angle = math.fmod(start_angle, 2.0 * math.pi)
    if sweep_angle >=  2.0 * math.pi:
        sweep_angle =  2.0 * math.pi
    if sweep_angle <= -2.0 * math.pi:
        sweep_angle = -2.0 * math.pi

    V = arc( cx, cy, rx, ry, start_angle, start_angle+sweep_angle, sweep_flag )
    c = math.cos(angle)
    s = math.sin(angle)
    X,Y = V[:,0]-cx, V[:,1]-cy
    V[:,0] = c*X - s*Y + cx
    V[:,1] = s*X + c*Y + cy
    return V
