# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

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
    def __init__(self, vcode=None, fcode=None):
        Program.__init__(self)

        self.changed = EventEmitter(source=self, type='program_change')

        # Cache state of Variables so we know which ones require update
        self._variable_state = {}

        self.vert = vcode
        self.frag = fcode

    @property
    def vert(self):
        return self._vert

    @vert.setter
    def vert(self, vcode):
        if hasattr(self, '_vert') and self._vert is not None:
            self._vert.changed.disconnect((self, '_source_changed'))

        self._vert = vcode
        if self._vert is None:
            return

        vcode = preprocess(vcode)
        self._vert = MainFunction(vcode)
        self._vert.changed.connect((self, '_source_changed'))

        self._need_build = True
        self.changed(code_changed=True, value_changed=False)

    @property
    def frag(self):
        return self._frag

    @frag.setter
    def frag(self, fcode):
        if hasattr(self, '_frag') and self._frag is not None:
            self._frag.changed.disconnect((self, '_source_changed'))

        self._frag = fcode
        if self._frag is None:
            return

        fcode = preprocess(fcode)
        self._frag = MainFunction(fcode)
        self._frag.changed.connect((self, '_source_changed'))

        self._need_build = True
        self.changed(code_changed=True, value_changed=False)

    def prepare(self):
        """ Prepare the Program so we can set attributes and uniforms.
        """
        pass
        # todo: remove!

    def _source_changed(self, ev):
        logger.debug("ModularProgram source changed: %s", self)
        if ev.code_changed:
            self._need_build = True
        self.changed(code_changed=ev.code_changed, 
                     value_changed=ev.value_changed)
    
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
            logger.debug("    %s = %s", name, dep.value)
            state_id = dep.state_id
            if self._variable_state.get(name, None) != state_id:
                self[name] = dep.value
                self._variable_state[name] = state_id
