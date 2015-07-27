# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import logging

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
    def __init__(self, vcode='', fcode=''):
        Program.__init__(self)

        self.changed = EventEmitter(source=self, type='program_change')

        # Cache state of Variables so we know which ones require update
        self._variable_state = {}

        self._vert = MainFunction('')
        self._frag = MainFunction('')
        self._vert._dependents[self] = None
        self._frag._dependents[self] = None

        self.vert = vcode
        self.frag = fcode

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

    def _dep_changed(self, dep, code_changed=False, value_changed=False):
        if code_changed and logger.level <= logging.DEBUG:
            import traceback
            logger.debug("ModularProgram changed: %s   source=%s, values=%s", 
                         self, code_changed, value_changed)
            traceback.print_stack()
            
        if code_changed:
            self._need_build = True
        self.changed(code_changed=code_changed, 
                     value_changed=value_changed)
    
    def draw(self, *args, **kwargs):
        self.build_if_needed()
        Program.draw(self, *args, **kwargs)

    def build_if_needed(self):
        """ Reset shader source if necesssary.
        """
        if self._need_build:
            self._build()
            self._need_build = False
        self.update_variables()

    def _build(self):
        logger.debug("Rebuild ModularProgram: %s", self)
        self.compiler = Compiler(vert=self.vert, frag=self.frag)
        code = self.compiler.compile()
        self.set_shaders(code['vert'], code['frag'])
        logger.debug('==== Vertex Shader ====\n\n%s\n', code['vert'])
        logger.debug('==== Fragment shader ====\n\n%s\n', code['frag'])
        # Note: No need to reset _variable_state, gloo.Program resends
        # attribute/uniform data on setting shaders

    def update_variables(self):
        # Clear any variables that we may have set another time.
        # Otherwise we get lots of warnings.
        self._pending_variables = {}
        # set all variables
        settable_vars = 'attribute', 'uniform'
        logger.debug("Apply variables:")
        deps = self.vert.dependencies() + self.frag.dependencies()
        for dep in deps:
            if not isinstance(dep, Variable) or dep.vtype not in settable_vars:
                continue
            name = self.compiler[dep]
            state_id = dep.state_id
            if self._variable_state.get(name, None) != state_id:
                self[name] = dep.value
                self._variable_state[name] = state_id
                logger.debug("    %s = %s **", name, dep.value)
            else:
                logger.debug("    %s = %s", name, dep.value)
