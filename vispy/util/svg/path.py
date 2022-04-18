# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import re
import math
import numpy as np

from . import geometry
from . geometry import epsilon
from . transformable import Transformable


# ----------------------------------------------------------------- Command ---
class Command(object):

    def __repr__(self):
        s = '%s ' % self._command
        for arg in self._args:
            s += "%.2f " % arg
        return s

    def origin(self, current=None, previous=None):
        relative = self._command in "mlvhcsqtaz"

        if relative and current:
            return current
        else:
            return 0.0, 0.0


# -------------------------------------------------------------------- Line ---
class Line(Command):

    def __init__(self, x=0, y=0, relative=True):
        self._command = 'l' if relative else 'L'
        self._args = [x, y]

    def vertices(self, current, previous=None):
        ox, oy = self.origin(current)
        x, y = self._args
        self.previous = x, y

        return (ox + x, oy + y),


# ------------------------------------------------------------------- VLine ---
class VLine(Command):

    def __init__(self, y=0, relative=True):
        self._command = 'v' if relative else 'V'
        self._args = [y]

    def vertices(self, current, previous=None):
        ox, oy = self.origin(current)
        y = self._args[0]
        self.previous = ox, oy + y

        return (ox, oy + y),


# ------------------------------------------------------------------- HLine ---
class HLine(Command):

    def __init__(self, x=0, relative=True):
        self._command = 'h' if relative else 'H'
        self._args = [x]

    def vertices(self, current, previous=None):
        ox, oy = self.origin(current)
        x = self._args[0]
        self.previous = ox + x, oy

        return (ox + x, oy),


# -------------------------------------------------------------------- Move ---
class Move(Command):

    def __init__(self, x=0, y=0, relative=True):
        self._command = 'm' if relative else 'M'
        self._args = [x, y]

    def vertices(self, current, previous=None):
        ox, oy = self.origin(current)
        x, y = self._args
        x, y = x + ox, y + oy
        self.previous = x, y
        return (x, y),


# ------------------------------------------------------------------- Close ---
class Close(Command):

    def __init__(self, relative=True):
        self._command = 'z' if relative else 'Z'
        self._args = []

    def vertices(self, current, previous=None):
        self.previous = current
        return []


# --------------------------------------------------------------------- Arc ---
class Arc(Command):

    def __init__(self, r1=1, r2=1, angle=2 * math.pi, large=True, sweep=True,
                 x=0, y=0, relative=True):
        self._command = 'a' if relative else 'A'
        self._args = [r1, r2, angle, large, sweep, x, y]

    def vertices(self, current, previous=None):
        ox, oy = self.origin(current)
        rx, ry, angle, large, sweep, x, y = self._args
        x, y = x + ox, y + oy
        x0, y0 = current
        self.previous = x, y
        vertices = geometry.elliptical_arc(
            x0, y0, rx, ry, angle, large, sweep, x, y)
        return vertices[1:]


# ------------------------------------------------------------------- Cubic ---
class Cubic(Command):

    def __init__(self, x1=0, y1=0, x2=0, y2=0, x3=0, y3=0, relative=True):
        self._command = 'c' if relative else 'C'
        self._args = [x1, y1, x2, y2, x3, y3]

    def vertices(self, current, previous=None):
        ox, oy = self.origin(current)
        x0, y0 = current
        x1, y1, x2, y2, x3, y3 = self._args
        x1, y1 = x1 + ox, y1 + oy
        x2, y2 = x2 + ox, y2 + oy
        x3, y3 = x3 + ox, y3 + oy
        self.previous = x2, y2
        vertices = geometry.cubic((x0, y0), (x1, y1), (x2, y2), (x3, y3))
        return vertices[1:]


# --------------------------------------------------------------- Quadratic ---
class Quadratic(Command):

    def __init__(self, x1=0, y1=0, x2=0, y2=0, relative=True):
        self._command = 'q' if relative else 'Q'
        self._args = [x1, y1, x2, y2]

    def vertices(self, current, last_control_point=None):
        ox, oy = self.origin(current)
        x1, y1, x2, y2 = self._args
        x0, y0 = current
        x1, y1 = x1 + ox, y1 + oy
        x2, y2 = x2 + ox, y2 + oy
        self.previous = x1, y1
        vertices = geometry.quadratic((x0, y0), (x1, y1), (x2, y2))

        return vertices[1:]


# ------------------------------------------------------------- SmoothCubic ---
class SmoothCubic(Command):

    def __init__(self, x2=0, y2=0, x3=0, y3=0, relative=True):
        self._command = 's' if relative else 'S'
        self._args = [x2, y2, x3, y3]

    def vertices(self, current, previous):
        ox, oy = self.origin(current)
        x0, y0 = current
        x2, y2, x3, y3 = self._args
        x2, y2 = x2 + ox, y2 + oy
        x3, y3 = x3 + ox, y3 + oy
        x1, y1 = 2 * x0 - previous[0], 2 * y0 - previous[1]
        self.previous = x2, y2
        vertices = geometry.cubic((x0, y0), (x1, y1), (x2, y2), (x3, y3))

        return vertices[1:]


# --------------------------------------------------------- SmoothQuadratic ---
class SmoothQuadratic(Command):

    def __init__(self, x2=0, y2=0, relative=True):
        self._command = 't' if relative else 'T'
        self._args = [x2, y2]

    def vertices(self, current, previous):
        ox, oy = self.origin(current)
        x2, y2 = self._args
        x0, y0 = current
        x1, y1 = 2 * x0 - previous[0], 2 * y0 - previous[1]
        x2, y2 = x2 + ox, y2 + oy
        self.previous = x1, y1
        vertices = geometry.quadratic((x0, y0), (x1, y1), (x2, y2))

        return vertices[1:]


# -------------------------------------------------------------------- Path ---
class Path(Transformable):

    def __init__(self, content=None, parent=None):
        Transformable.__init__(self, content, parent)
        self._paths = []

        if not isinstance(content, str):
            content = content.get("d", "")

        commands = re.compile(
            r"(?P<command>[MLVHCSQTAZmlvhcsqtaz])"
            r"(?P<points>[+\-0-9.e, \n\t]*)")

        path = []
        for match in re.finditer(commands, content):
            command = match.group("command")
            points = match.group("points").replace(',', ' ')
            points = [float(v) for v in points.split()]
            relative = command in "mlvhcsqtaz"
            command = command.upper()

            while len(points) or command == 'Z':
                if command == 'M':
                    if len(path):
                        self._paths.append(path)
                    path = []
                    path.append(Move(*points[:2], relative=relative))
                    points = points[2:]
                elif command == 'L':
                    path.append(Line(*points[:2], relative=relative))
                    points = points[2:]
                elif command == 'V':
                    path.append(VLine(*points[:1], relative=relative))
                    points = points[1:]
                elif command == 'H':
                    path.append(HLine(*points[:1], relative=relative))
                    points = points[1:]
                elif command == 'C':
                    path.append(Cubic(*points[:6], relative=relative))
                    points = points[6:]
                elif command == 'S':
                    path.append(SmoothCubic(*points[:4], relative=relative))
                    points = points[4:]
                elif command == 'Q':
                    path.append(Quadratic(*points[:4], relative=relative))
                    points = points[4:]
                elif command == 'T':
                    path.append(
                        SmoothQuadratic(*points[2:], relative=relative))
                    points = points[2:]
                elif command == 'A':
                    path.append(Arc(*points[:7], relative=relative))
                    points = points[7:]
                elif command == 'Z':
                    path.append(Close(relative=relative))
                    self._paths.append(path)
                    path = []
                    break
                else:
                    raise RuntimeError(
                        "Unknown SVG path command(%s)" % command)

        if len(path):
            self._paths.append(path)

    def __repr__(self):
        s = ""
        for path in self._paths:
            for item in path:
                s += repr(item)
        return s

    @property
    def xml(self):
        return self._xml()

    def _xml(self, prefix=""):
        s = prefix + "<path "
        s += 'id="%s" ' % self._id
        s += self._style.xml
        s += '\n'
        t = '     ' + prefix + ' d="'
        s += t
        prefix = ' ' * len(t)
        first = True
        for i, path in enumerate(self._paths):
            for j, item in enumerate(path):
                if first:
                    s += repr(item)
                    first = False
                else:
                    s += prefix + repr(item)
                if i < len(self._paths) - 1 or j < len(path) - 1:
                    s += '\n'
        s += '"/>\n'
        return s

    @property
    def vertices(self):
        self._vertices = []
        current = 0, 0
        previous = 0, 0

        for path in self._paths:
            vertices = []
            for command in path:
                V = command.vertices(current, previous)
                previous = command.previous
                vertices.extend(V)
                if len(V) > 0:
                    current = V[-1]
                else:
                    current = 0, 0

            closed = False
            if isinstance(command, Close):
                closed = True
                if len(vertices) > 2:
                    d = geometry.calc_sq_distance(vertices[-1][0], vertices[-1][1],  # noqa
                                                  vertices[0][0], vertices[0][1])  # noqa
                    if d < epsilon:
                        vertices = vertices[:-1]

            # Apply transformation
            V = np.ones((len(vertices), 3))
            V[:, :2] = vertices
            V = np.dot(V, self.transform.matrix.T)
            V[:, 2] = 0
            self._vertices.append((V, closed))

        return self._vertices
