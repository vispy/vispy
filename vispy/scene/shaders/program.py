# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division, print_function
import re

from ...gloo import Program, VertexShader, FragmentShader
from .function import Function, FunctionChain
from . import parsing
from ...util import logger
from ...ext.six import string_types


"""
API issues to work out:


Need to think more about efficiency:
    - ability to re-assign hooks or modify chains and have dependencies
      automatically re-calculated
        => need to track {dep: [refs...]} so that deps are only removed when no
           more referrers are present.
        => same goes for shared variables..
    - ability to assign new program variable values to an existing program
    - caching compilation of individual functions if possible
    - remember variable name assignments, only recompute when necessary.
    - Ideally, one Function may appear in multiple ModularPrograms
      (with the same variable assignments each time)

Need ability to assign function calls to program variables
    (specifically, to replace uniforms with texture lookup for Collections)

Possibly move hook/chain features out to ModularShader; keep ModularProgram
more focused on compilation.
    Maybe ModularShader is a subclass of Function? Or vice-versa?


"""
class ModularProgram(Program):
    """
    Shader program that is composed of main shader functions combined with
    any number of Functions.

    """
    def __init__(self, vmain, fmain):
        Program.__init__(self)
        self.vmain = vmain
        self.fmain = fmain

        # keep track of attached shaders
        self._vshader = None
        self._fshader = None

        # Cache state of Variables so we know which ones require update
        self._variable_state = {}

    def prepare(self):
        """ Prepare the Program so we can set attributes and uniforms.
        """
        # TEMP function to fix sync issues for now
        self._create()
        self._build()
        self._need_build = False
        
    def _build(self):
        # Generate all code
        self.vmain.link(self.fmain)
        self.vcode = self.vmain.compile()
        self.fcode = self.fmain.compile()

        # Detach old shaders
        if self._vshader is not None:
            self.detach([self._vshader, self._fshader])
            self._vshader = self._fshader = None

        # Attach new shaders
        vs = VertexShader(self.vcode)
        fs = FragmentShader(self.fcode)
        self.attach([vs, fs])
        self._vshader = vs
        self._fshader = fs

        # and continue.
        super(ModularProgram, self)._build()

    def _activate_variables(self):
        # set all variables
        self._apply_variables()
        
        super(ModularProgram, self)._activate_variables()        

    def _apply_variables(self):
        """
        Apply all program variables that are carried by the components of this
        program.
        """
        logger.debug("Apply variables:")
        for name, spec in self.namespace.items():
            if isinstance(spec, Function) or spec.vtype == 'varying':
                continue
            logger.debug("    %s = %s" % (name, spec.value))
            state_id = spec.state_id
            if self._variable_state.get(name, None) != state_id:
                self[name] = spec.value
                self._variable_state[name] = state_id
