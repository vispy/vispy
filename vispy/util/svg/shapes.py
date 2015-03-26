# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------


class Rect(object):

    def __init__(self, x=0, y=0, width=1, height=1, rx=0, ry=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rx = rx
        self.ry = ry

    def parse(self, expression):
        """ """


class Line(object):

    def __init__(self, x1=0, y1=0, x2=0, y2=0):
        self.x1 = x2
        self.y1 = y2
        self.x2 = x2
        self.y2 = y2


class Circle(object):

    def __init__(self, cx=0, cy=0, r=1):
        self.cx = cx
        self.cy = cy
        self.r = r


class Ellipse(object):

    def __init__(self, cx=0, cy=0, rx=1, ry=1):
        self.cx = cx
        self.cy = cy
        self.rx = rx
        self.ry = ry


class Polygon(object):

    def __init__(self, points=[]):
        self.points = points


class Polyline(object):

    def __init__(self, points=[]):
        self.points = points
