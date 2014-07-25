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
        self.vert.link(self.frag)

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
    
    def __setitem__(self, name, value):
        # store variables here temporarily; they will be uploaded before draw.
        self.vert[name] = value
        
    def _build(self):
        if self.vert.ischanged():
            logger.debug('==== Vertex Shader ====')
            code = str(self.vert)
            logger.debug(code)
            self.shaders[0].code = code
            self._create_variables()  # force update
        
        if self.frag.ischanged():
            logger.debug('==== Fragment shader ====')
            code = str(self.frag)
            logger.debug(code)
            self.shaders[1].code = code
            self._create_variables()  # force update

        # and continue.
        super(ModularProgram, self)._build()

    def _activate_variables(self):
        # set all variables
        logger.debug("Apply variables:")
        for var in self.vert.get_variables():
            name = var.name
            logger.debug("    %s = %s" % (name, var.value))
            if var.vtype in ('attribute', 'uniform'):
                state_id = var.state_id
                if self._variable_state.get(name, None) != state_id:
                    Program.__setitem__(self, name, var.value)
                    self._variable_state[name] = state_id
        
        super(ModularProgram, self)._activate_variables()        
