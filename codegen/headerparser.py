# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Code to parse a header file.
"""

import os
import sys


TYPEMAP = {
    'GLenum': 'int (GLenum)',
}


def getwords(line):
    """ Get words on a line.
    """
    line = line.replace('\t', ' ').strip()
    return [w for w in line.split(' ') if w]


# Keep track of all constants in case they are "reused" in a header file
CONSTANTS = {}


class Parser:

    """ Class to parse header files.
    """

    def __init__(self, header_file, parse_now=True):
        # Get filenames for C and Py
        self._c_fname = c_fname = os.path.split(header_file)[1]

        # Get absolute filenames
        self._c_filename = header_file  # os.path.join(SCRIPT_DIR, c_fname)

        # Init output
        self.definitions = []
        self.functionDefs = []
        self.constantDefs = []

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
        self.definitions.append(definition)
        if isinstance(definition, FunctionDefinition):
            self.functionDefs.append(definition)
        elif isinstance(definition, ConstantDefinition):
            self.constantDefs.append(definition)

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
            elif (line.startswith('GLAPI') or
                    line.startswith('GL_APICALL') or
                    line.startswith('WINGDIAPI')):
                while ')' not in line:
                    line += self._get_line()
                #self += self.handle_function(line)
                self += FunctionDefinition(line)

        # Remove invalid defs
        self.definitions = [d for d in self.definitions if d.isvalid]
        self.functionDefs = [d for d in self.functionDefs if d.isvalid]
        self.constantDefs = [d for d in self.constantDefs if d.isvalid]

        # Resolve multipe functions that are really the same
        self.functionDefs.sort(key=lambda x: x.cname)
        keyDef = None
        for funcDef in self.functionDefs:
            if keyDef is not None:
                extrachars = funcDef.matchKeyName(keyDef.keyname)
                if extrachars:
                    funcDef.group = True
                    if not keyDef.group:
                        keyDef.group = [keyDef]
                    keyDef.group.append(funcDef)
                    continue
            if funcDef.extrachars:
                # This may be a key def
                keyDef = funcDef
            else:
                keyDef = None

        # Process all definitions
        for definition in self.definitions:
            if definition.isvalid:
                definition.process()

        # Get some stats
        for funcDef in self.functionDefs:
            for arg in funcDef.args:
                self.stat_types.add(arg.ctype)

        # Show stats
        n1 = len([d for d in self.constantDefs])
        n2 = len([d for d in self.functionDefs if d.group is not True])
        n3 = len([d for d in self.functionDefs if isinstance(d.group, list)])
        n4 = len([d for d in self.functionDefs if d.group is True])
        print(
            'Found %i constants and %i unique functions (%i groups contain %i functions)").' %
            (n1, n2, n3, n4))

        print('C-types found in args:', self.stat_types)

    @property
    def constant_names(self):
        return set([d.cname for d in self.constantDefs])

    @property
    def function_names(self):
        return set([d.cname for d in self.functionDefs])

    def show_groups(self):
        for d in self.functionDefs:
            if isinstance(d.group, list):
                print(d.keyname)
                for d2 in d.group:
                    print('  ', d2.cname)


class Definition:

    """ Abstract class to represent a constant or function definition.
    """

    def __init__(self, line):
        self.line = line
        self.isvalid = True
        self.comment = ''
        self.cname = ''
        self.parse_line(line)

    def parse_line(self, line):
        # Do initial parsing of the incoming line
        # (which may be multiline actually)
        pass

    def process(self):
        # Do more parsing of this definition
        pass


class ConstantDefinition(Definition):

    def parse_line(self, line):
        """ Set cname and value attributes.
        """
        self.value = None
        line = line.split('/*', 1)[0]
        _, *args = getwords(line)
        self.isvalid = False
        if len(args) == 1:
            pass
        elif len(args) == 2:
            # Set name
            self.cname, val = args
            self.isvalid = bool(self.cname)
            # Set value
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
        else:
            print('Dont know what to do with "%s"' % line)

        if self.value is not None:
            CONSTANTS[self.cname] = self.value

    def process(self):
        pass  # We did all that we needed to do


class FunctionDefinition(Definition):

    def parse_line(self, line):
        """ Set cname, keyname, cargs attributes.
        """
        # Parse components
        beforeBrace, args = line.split('(', 1)
        betweenBraces, _ = args.split(')', 1)
        *prefix, name = getwords(beforeBrace)

        # Store name
        self.cname = name

        # Possibly, this function belongs to a collection of similar functions,
        # which we are going to replace with one function in Python.
        self.keyname = self.cname.rstrip('v').rstrip('bsifd').rstrip('1234')
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
        if self.cname.startswith(keyname):
            extrachars = self.cname[len(keyname):]
            if all([(c in 'vbsuifd1234') for c in extrachars]):
                return extrachars

    def count_input_args(self):
        return len([arg for arg in self.args if arg.pyinput])

    def count_output_args(self):
        return len([arg for arg in self.args if (not arg.pyinput)])

    def process(self):

        # Is one of the inputs really an output?
        if self.cname.lower().startswith('glget'):
            if not self.count_output_args():
                args = [arg for arg in args if arg.isptr]
                if len(args) == 1:
                    args[0].pyinput = False
                else:
                    print(
                        'Warning: cannot determine py-output for %s' %
                        self.name)

        # Build Python function signature
        pyargs = ', '.join([arg.name for arg in self.args if arg.pyinput])
        #defline = 'def %s(%s):' % (self.pyname, pyargs)
        # ... not here


class Argument:

    """ Input or output argument.
    """

    def __init__(self, argAsString, cinput=True):
        # Parse string
        components = [c for c in argAsString.split(' ') if c]
        if len(components) == 1:
            name = components[0]
            type = 'unknown'
        else:
            name = components[-1]
            type = components[-2]
        # Store stuff
        self.orig = tuple(components)
        self.name = name.lstrip('*')
        self.isptr = len(name) - len(self.name)  # Number of stars
        self.ctype = type
        self.typedes = TYPEMAP.get(type, type)
        self.pytype = self.typedes.split(' ')[0]
        # Status flags
        self.cinput = cinput
        self.pyinput = cinput  # May be modified


if __name__ == '__main__':
    THISDIR = os.path.abspath(os.path.dirname(__file__))

    # Some tests ...
    gl2 = Parser(os.path.join(THISDIR, 'headers', 'gl2.h'))
    import OpenGL.GL
    pygl = set(dir(OpenGL.GL))

    # Test if all functions are in pyopengl
    print('Not in pyopengl:', gl2.function_names.difference(pygl))

    # Test if constant match with these in pyopengl
    for d in gl2.constantDefs:
        v1 = d.value
        try:
            v2 = getattr(OpenGL.GL, d.cname)
        except AttributeError:
            print(d.cname, 'is not in pyopengl')
        else:
            if v1 != v2:
                print(d.cname, 'does not match: %r vs %r' % (v1, int(v2)))
