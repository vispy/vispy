# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division, print_function

from ...gloo import Program
from ...util import logger
from ...util.event import EventEmitter
from ...ext.six import string_types  # noqa
from .function import MainFunction, Variable
from .compiler import Compiler


class ModularProgram(Program):
    """
    Shader program using Function instances as basis for its shaders.
    
    Automatically rebuilds program when functions have changed and uploads 
    program variables.
    """
    def __init__(self, vcode, fcode):
        Program.__init__(self, '', '')
        
        self.changed = EventEmitter(source=self, type='program_change')
        
        self.vert = MainFunction(vcode)
        self.frag = MainFunction(fcode)
        self.vert.changed.connect(self._source_changed)
        self.frag.changed.connect(self._source_changed)
        
        # Cache state of Variables so we know which ones require update
        self._variable_state = {}
        
        self._need_build = True

    def prepare(self):
        """ Prepare the Program so we can set attributes and uniforms.
        """
        # TEMP function to fix sync issues for now
        self._create()
        if self._need_build:
            self._build()
            self._need_build = False
    
    def _source_changed(self, ev):
        logger.debug("ModularProgram source changed: %s" % self)
        if ev.code_changed:
            self._need_build = True
        self.changed()
        
    def _build(self):
        logger.debug("Rebuild ModularProgram: %s" % self)
        self.compiler = Compiler(vert=self.vert, frag=self.frag)
        code = self.compiler.compile()
        self.shaders[0].code = code['vert']
        self.shaders[1].code = code['frag']
        
        logger.debug('==== Vertex Shader ====\n\n' + code['vert'] + "\n")
        logger.debug('==== Fragment shader ====\n\n' + code['frag'] + "\n")
        
        self._create_variables()  # force update
        self._variable_state = {}
        
        # and continue.
        super(ModularProgram, self)._build()

    def _activate_variables(self):
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
        
        super(ModularProgram, self)._activate_variables()        
