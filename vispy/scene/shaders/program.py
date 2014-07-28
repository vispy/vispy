# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division, print_function
import re

from ...gloo import Program, VertexShader, FragmentShader
from .function2 import Function
from . import parsing
from ...util import logger
from ...ext.six import string_types


class ModularProgram(Program):
    """
    Shader program using Function instances as basis for its shaders.
    
    Automatically rebuilds program when functions have changed and uploads 
    program variables.
    """
    def __init__(self, vcode, fcode):
        Program.__init__(self, '', '')
        
        self.vert = Function(vcode)
        self.frag = Function(fcode)
        
        # Cache state of Variables so we know which ones require update
        self._variable_state = {}

    def prepare(self):
        """ Prepare the Program so we can set attributes and uniforms.
        """
        pass  # is this still needed?
        # TEMP function to fix sync issues for now
        #self._create()
        #self._build()
        #self._need_build = False
    
    def _source_changed(self):
        self._need_build = True
        
    def _build(self):
        self.compiler = Compiler(vert=self.vmain, frag=self.fmain)
        code = self.compiler.compile()
        self.shaders[0].code = code['vert']
        self.shaders[1].code = code['frag']
        self._create_variables()  # force update
        self._variable_state = {}
        
        #if self.vert.ischanged():
            #logger.debug('==== Vertex Shader ====')
            #code = str(self.vert)
            #logger.debug(code)
            #self.shaders[0].code = code
            #self._create_variables()  # force update
        
        #if self.frag.ischanged():
            #logger.debug('==== Fragment shader ====')
            #code = str(self.frag)
            #logger.debug(code)
            #self.shaders[1].code = code
            #self._create_variables()  # force update

        # and continue.
        super(ModularProgram, self)._build()

    def _activate_variables(self):
        # set all variables
        logger.debug("Apply variables:")
        deps = self.vmain.dependencies() + self.fmain.dependencies()
        for dep in deps:
            if not isinstance(dep, Variable) or dep.type == 'varying':
                continue
            name = self.compiler[var]
            logger.debug("    %s = %s" % (name, var.value))
            state_id = var.state_id
            if self._variable_state.get(name, None) != state_id:
                self[name] = var.value
                self._variable_state[name] = state_id
        
        super(ModularProgram, self)._activate_variables()        
