import weakref


class MultiProgram(object):
    """A collection of ModularPrograms that emulates the API of a single
    ModularProgram. 

    A single Visual is often drawn in many different ways--viewed under
    different transforms, with different clipping boundaries, or with different
    colors as in picking and anaglyph stereo. Each draw may require a different
    program. To simplify this process, MultiProgram exposes an API that looks
    very much like a single ModularProgram, but internally manages many
    programs.
    """
    def __init__(self, vcode=None, fcode=None):
        self._vcode = vcode
        self._fcode = fcode
        self._programs = weakref.weakValueDictionary()
        self._set_items = {}
        self._next_prog_id = 0
        self._vert = MultiShader(self, 'vert')
        self._frag = MultiShader(self, 'frag')

    def add_program(self, name=None):
        """Create a program and add it to this MultiProgram.
        
        It is the caller's responsibility to keep a reference to the returned 
        program.
        
        The *name* must be unique, but is otherwise arbitrary and used for 
        debugging purposes.
        """
        if name is None:
            name = 'program' + str(self._next_prog_id)
            self._next__progid += 1
                
        if name in self._programs:
            raise KeyError("Program named '%s' already exists." % name)
        
        # create a program and update it to look like the rest
        prog = ModularProgram(self._vcode, self._fcode)
        for key, val in self._set_items.items():
            prog[key] = val
        self.frag._new_program(prog)
        self.vert._new_program(prog)
        
        self._programs[name] = prog
        return prog

    @property
    def vert(self):
        return self._vert

    #@vert.setter
    #def vert(self, vcode):

    @property
    def frag(self):
        return self._frag

    #@frag.setter
    #def frag(self, fcode):

    def __getitem__(self, key):
        return self._set_items[key]
        
    def __setitem__(self, key, value):
        self._set_items[key] = value
        for program in self._programs.values():
            program[key] = value


class MultiShader(object):
    """Emulates the API of a MainFunction while wrapping all programs in a 
    MultiProgram.
    """
    def __getitem__(self, key):
        
        
    def __setitem__(self, key, value):
        
    