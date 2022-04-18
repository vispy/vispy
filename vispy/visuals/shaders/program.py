# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import logging
from weakref import WeakKeyDictionary

from ...gloo import Program
from ...gloo.preprocessor import preprocess
from ...util import logger
from ...util.event import EventEmitter
from .function import MainFunction
from .variable import Variable
from .compiler import Compiler


class ModularProgram(Program):
    """
    Shader program using Function instances as basis for its shaders.

    Automatically rebuilds program when functions have changed and uploads
    program variables.
    """

    def __init__(self, vcode='', fcode='', gcode=None):
        Program.__init__(self)

        self.changed = EventEmitter(source=self, type='program_change')

        # Cache state of Variables so we know which ones require update
        self._variable_cache = WeakKeyDictionary()

        # List of settable variables to be checked for value changes
        self._variables = []

        self._vert = MainFunction('vertex', '')
        self._frag = MainFunction('fragment', '')
        self._vert._dependents[self] = None
        self._frag._dependents[self] = None
        self._geom = None

        self.vert = vcode
        self.frag = fcode
        self.geom = gcode

    @property
    def vert(self):
        return self._vert

    @vert.setter
    def vert(self, vcode):
        vcode = preprocess(vcode)
        self._vert.code = vcode
        self._need_build = True
        self.changed(code_changed=True, value_changed=False)

    @property
    def frag(self):
        return self._frag

    @frag.setter
    def frag(self, fcode):
        fcode = preprocess(fcode)
        self._frag.code = fcode
        self._need_build = True
        self.changed(code_changed=True, value_changed=False)

    @property
    def geom(self):
        return self._geom

    @geom.setter
    def geom(self, gcode):
        if gcode is None:
            self._geom = None
            return
        gcode = preprocess(gcode)
        if self._geom is None:
            self._geom = MainFunction('geometry', '')
            self._geom._dependents[self] = None
        self._geom.code = gcode
        self._need_build = True
        self.changed(code_changed=True, value_changed=False)

    def _dep_changed(self, dep, code_changed=False, value_changed=False):
        if code_changed and logger.level <= logging.DEBUG:
            logger.debug("ModularProgram changed: %s   source=%s, values=%s", 
                         self, code_changed, value_changed)
            import traceback
            traceback.print_stack()

        if code_changed:
            self._need_build = True
        self.changed(code_changed=code_changed, 
                     value_changed=value_changed)

    def draw(self, *args, **kwargs):
        self.build_if_needed()
        self.update_variables()
        Program.draw(self, *args, **kwargs)

    def build_if_needed(self):
        """Reset shader source if necesssary."""
        if self._need_build:
            self._build()

            # after recompile, we need to upload all variables again
            # (some variables may have changed name)
            self._variable_cache.clear()

            # Collect a list of all settable variables
            settable_vars = 'attribute', 'uniform', 'in'
            deps = [d for d in self.vert.dependencies() if (
                isinstance(d, Variable) and d.vtype in settable_vars)]
            deps += [d for d in self.frag.dependencies() if (
                isinstance(d, Variable) and d.vtype == 'uniform')]
            if self.geom is not None:
                deps += [d for d in self.geom.dependencies() if (
                    isinstance(d, Variable) and d.vtype == 'uniform')]
            self._variables = deps

            self._need_build = False

    def _build(self):
        logger.debug("Rebuild ModularProgram: %s", self)
        shaders = {'vert': self.vert, 'frag': self.frag}
        if self.geom is not None:
            shaders['geom'] = self.geom
        self.compiler = Compiler(**shaders)
        code = self.compiler.compile()

        # Update shader code, but don't let the program update variables yet 
        code['update_variables'] = False
        self.set_shaders(**code)

        logger.debug('==== Vertex Shader ====\n\n%s\n', code['vert'])
        if 'geom' in code:
            logger.debug('==== Geometry shader ====\n\n%s\n', code['geom'])
        logger.debug('==== Fragment shader ====\n\n%s\n', code['frag'])

    def update_variables(self):
        # Set any variables that have a new value
        logger.debug("Apply variables:")
        for dep in sorted(self._variables, key=lambda d: self.compiler[d]):
            name = self.compiler[dep]
            state_id = dep.state_id
            if self._variable_cache.get(dep, None) != state_id:
                self[name] = dep.value
                self._variable_cache[dep] = state_id
                logger.debug("    %s = %s **", name, dep.value)
            else:
                logger.debug("    %s = %s", name, dep.value)

        # Process any pending variables and discard anything else that is
        # not active in the program (otherwise we get lots of warnings).
        self._process_pending_variables()
        logger.debug("Discarding unused variables before draw: %s" % 
                     self._pending_variables.keys())
        self._pending_variables = {}
