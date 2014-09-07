# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Code to parse a header file and create a list of constants,
functions (with arguments). This information can then be used to
autogenerate our OpenGL API.
"""

import os
import sys


def getwords(line):
    """ Get words on a line.
    """
    line = line.replace('\t', ' ').strip()
    return [w for w in line.split(' ') if w]


# Keep track of all constants in case they are "reused" (i.e. aliases)
CONSTANTS = {}


class Parser:
    """ Class to parse header files. It can deal with gl2.h and webgl.idl,
    as well as some desktop OpenGL header files. It produces a list of
    ConstantDefition objects and FunctionDefinition objects, which can 
    be accessed via a dict.
    """

    def __init__(self, header_file, parse_now=True):
        # Get filenames for C and Py
        self._c_fname = c_fname = os.path.split(header_file)[1]

        # Get absolute filenames
        self._c_filename = header_file

        # Init intermediate results
        self._functionDefs = []
        self._constantDefs = []

        # Init output
        self._functions = {}
        self._constants = {}

        # We are aware of the line number
        self._linenr = 0

        # Some stats
        self.stat_types = set()

        if parse_now:
            self.parse()

    def __iadd__(self, definition):
        """ Add an output line. Can be multiple lines.
        """
        # Create comment
        definition.comment = 'line %i of %s' % (self._linenr, self._c_fname)
        # Add to lists
        if isinstance(definition, FunctionDefinition):
            self._functionDefs.append(definition)
        elif isinstance(definition, ConstantDefinition):
            self._constantDefs.append(definition)
        return self

    def _get_line(self):
        # Get a stripped line, and keep track of line nr, skip empty lines
        line = ''
        while not line:
            line = self._file.readline()
            if not line:
                raise StopIteration()
            line = line.strip()
            self._linenr += 1
        return line

    def _get_lines(self):
        # Easy iterator
        while True:
            yield self._get_line()

    def parse(self):
        """ Parse the header file!
        """

        # Open file
        self._file = open(self._c_filename, 'rt', encoding='utf-8')

        # Parse the file
        for line in self._get_lines():
            if line.startswith('#define'):
                self += ConstantDefinition(line)
            elif line.startswith('const GLenum'):
                self += ConstantDefinition(line)
            elif '(' in line:
                while ')' not in line:
                    line += self._get_line()
                if line.endswith(');'):
                    self += FunctionDefinition(line)

        # Remove invalid defs
        self._functionDefs = [d for d in self._functionDefs if d.isvalid]
        self._constantDefs = [d for d in self._constantDefs if d.isvalid]

        # Collect multipe similar functions in groups
        self._functionDefs.sort(key=lambda x: x.glname)
        keyDef = None
        keyDefs = []
        for funcDef in [f for f in self._functionDefs]:
            # Check if we need a new keydef
            if funcDef.extrachars:
                # Create new keydef or use old one?
                if keyDef and keyDef.glname == funcDef.keyname:
                    pass  # Keep same keydef
                else:
                    keyDef = FunctionGroup(funcDef.line)  # New keydef
                    keyDef._set_name(funcDef.keyname)
                    keyDefs.append(keyDef)
                # Add to group
                keyDef.group.append(funcDef)
        # Process function groups
        for keyDef in keyDefs:
            if len(keyDef.group) > 1:
                self._functionDefs.append(keyDef)
                for d in keyDef.group:
                    self._functionDefs.remove(d)

        # Sort constants and functions
        self._functionDefs.sort(key=lambda x: x.glname)
        self._constantDefs.sort(key=lambda x: x.glname)

        # Get dicts
        for definition in self._functionDefs:
            self._functions[definition.shortname] = definition
        for definition in self._constantDefs:
            self._constants[definition.shortname] = definition

        # Get some stats
        for funcDef in self._functionDefs:
            for arg in funcDef.args:
                self.stat_types.add(arg.ctype)

        # Show stats
        n1 = len([d for d in self._constantDefs])
        n2 = len([d for d in self._functionDefs])
        n3 = len([d for d in self._functionDefs if d.group])
        n4 = sum([len(d.group) for d in self._functionDefs if d.group])
        print('Found %i constants and %i unique functions (%i groups contain %i functions)").' % (
            n1, n2, n3, n4))

        print('C-types found in args:', self.stat_types)

    @property
    def constant_names(self):
        """ Sorted list of constant names.
        """
        return [d.shortname for d in self._constantDefs]

    @property
    def function_names(self):
        """ Sorted list of function names.
        """
        return [d.shortname for d in self._functionDefs]

    @property
    def constants(self):
        """ Dict with all the constants.
        """
        return self._constants

    @property
    def functions(self):
        """ Dict witj all the functions.
        """
        return self._functions

    def show_groups(self):
        for d in self._functionDefs:
            if isinstance(d.group, list):
                print(d.keyname)
                for d2 in d.group:
                    print('  ', d2.glname)



class Definition:
    """ Abstract class to represent a constant or function definition.
    """

    def __init__(self, line):
        self.line = line
        self.isvalid = True
        self.comment = ''
        self.oname = ''  # original name
        self.shortname = self.glname = ''  # short and long name
        self.parse_line(line)

    def parse_line(self, line):
        # Do initial parsing of the incoming line
        # (which may be multiline, actually)
        pass

    def _set_name(self, name):
        # Store original name
        self.oname = name
        # Store plain name
        if name.startswith('GL_'):
            name = name[3:]
        elif name.startswith('gl'):
            name = name[2].lower() + name[3:]
        self.shortname = name
        # Store gl name
        if name.upper() == name:
            name = 'GL_' + name
        else:
            name = 'gl' + name[0].upper() + name[1:]
        self.glname = name



class ConstantDefinition(Definition):

    def parse_line(self, line):
        """ Set cname and value attributes.
        """
        self.value = None
        line = line.split('/*', 1)[0]
        args = getwords(line)[1:]
        self.isvalid = False
        if len(args) == 1:
            pass
        elif len(args) == 2:
            # Set name
            name, val = args
            self.isvalid = bool(name)
            self._set_name(name)
            self._set_value_from_string(val)
        elif '=' in args:
            name, val = args[-3], args[-1]
            self.isvalid = bool(name)
            self._set_name(name)
            self._set_value_from_string(val)
        else:
            print('Dont know what to do with "%s"' % line)

        # For when this constant is reused to set another constant
        if self.value is not None:
            CONSTANTS[self.oname] = self.value

    def _set_value_from_string(self, val):
        # Set value
        val = val.strip(';')
        if val.startswith('0x'):
            self.value = int(val[2:].rstrip('ul'), 16)
        elif val[0] in '0123456789':
            self.value = int(val)
        elif val.startswith("'"):
            self.value = val
        elif val in CONSTANTS:
            self.value = CONSTANTS[val]
        else:
            print('Warning: Dont know what to do with "%s"' % line)



class FunctionDefinition(Definition):
    
    SKIPTYPECHARS = 'if'  # 'bsifd'
    ALLSKIPCHARS = SKIPTYPECHARS + 'v1234'
    
    def parse_line(self, line):
        """ Set cname, keyname, cargs attributes.
        The list of args always has one entry and the first entry is always
        the output (can be void).
        """
        # Parse components
        beforeBrace, args = line.split('(', 1)
        betweenBraces, _ = args.split(')', 1)
        outs = getwords(beforeBrace)
        prefix, name = outs[:-1], outs[-1]

        # Store name
        self._set_name(name)

        # Possibly, this function belongs to a collection of similar functions,
        # which we are going to replace with one function in Python.
        self.keyname = self.glname.rstrip('v').rstrip(self.SKIPTYPECHARS).rstrip('1234')
        self.extrachars = self.matchKeyName(self.keyname)
        
        # If this is a list, this instance represents the group
        # If this is True, this instance is in a group (but not the
        # representative)
        self.group = None

        # Create list of Argument instances
        self.cargs = [arg.strip() for arg in betweenBraces.split(',')]
        self.args = []
        # Set output arg
        self.args.append(Argument(' '.join(prefix), False))
        # Parse input arguments,
        for arg in self.cargs:
            if arg and arg != 'void':
                self.args.append(Argument(arg))

    def matchKeyName(self, keyname):
        if self.glname.startswith(keyname):
            extrachars = self.glname[len(keyname):]
            if all([(c in self.ALLSKIPCHARS) for c in extrachars]):
                return extrachars



class FunctionGroup(FunctionDefinition):

    def parse_line(self, line):
        FunctionDefinition.parse_line(self, line)
        self.group = []



class Argument:

    def __init__(self, argAsString, cinput=True):
        # Parse string
        components = [c for c in argAsString.split(' ') if c]
        if len(components) == 1:
            name = 'unknown_name'
            type = components[0]
        else:
            name = components[-1]
            type = components[-2]
            if 'const' in type:
                type = components[-3]  # glShaderSource has "const GLchar* const* string"
        # Store stuff
        self.orig = tuple(components)
        self.name = name.lstrip('*')
        self.isptr = argAsString.count('*')  # Number of stars
        self.ctype = type.strip('*') + '*'*self.isptr
        # Status flags
        self.cinput = cinput



if __name__ == '__main__':
    THISDIR = os.path.abspath(os.path.dirname(__file__))

    # Some tests ...
    gl2 = Parser(os.path.join(THISDIR, 'headers', 'gl2.h'))
    import OpenGL.GL
    pygl = set([name for name in dir(OpenGL.GL)])

    # Test if all functions are in pyopengl
    for keyfunc in gl2._functionDefs:
        group = keyfunc.group or [keyfunc]
        for f in group:
            if f.glname not in pygl:
                print('Not in pyopengl:', f.glname)

    # Test if constant match with these in pyopengl
    for d in gl2._constantDefs:
        v1 = d.value
        try:
            v2 = getattr(OpenGL.GL, d.glname)
        except AttributeError:
            print(d.glname, 'is not in pyopengl')
        else:
            if v1 != v2:
                print(d.glname, 'does not match: %r vs %r' % (v1, int(v2)))
