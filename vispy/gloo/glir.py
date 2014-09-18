""" Implementation to execute GL Intermediate Representation (GLIR)

"""

import sys

import numpy as np

from . import gl
from ..util import logger


class GlirQueue(object):
    """ Representation of a queue of GLIR commands. One instance of
    this class is attached to each context object, and gloo will post
    commands to this queue.
    
    Upon drawing (i.e. `Program.draw()`) The commands in the queue are
    pushed to an interpreter. This can be Python, JS, whatever. For
    now, each queue has a GlirParser object that does the interpretation
    in Python directly. This should later be replaced by some sort of
    plugin mechanism.
    """
    
    def __init__(self):
        self._commands = []
        self._parser = GlirParser()
        # todo: allow different kind of parsers, like a parser that sends to JS
    
    def command(self, *args):
        """ Send a command. See the command spec at:
        https://github.com/vispy/vispy/wiki/Spec.-Gloo-IR
        """
        self._commands.append(args)
    
    def show(self):
        """ Print the list of commands currently in the queue.
        """
        for command in self._commands:
            if command[0] is None:
                continue  # Skip nill commands 
            t = []
            for e in command:
                if isinstance(e, np.ndarray):
                    t.append('array %s' % str(e.shape))
                else:
                    t.append(e)
            print(tuple(t))
    
    def parse(self):
        """ Interpret all commands; do the OpenGL calls.
        """
        self._parser.parse(self._commands)
        self._commands = []


class GlirParser(object):
    """ A class for interpreting GLIR commands
    
    We make use of relatively light GLIR objects that are instantiated
    on CREATE commands. These objects are stored by their id in a
    dictionary so that commands like ACTIVATE and SET_DATA can easily
    be executed on the corresponding objects.
    """
    
    def __init__(self):
        self._objects = {}
        self._invalid_objects = set()
        self._classmap = {'VERTEXBUFFER': GlirVertexBuffer,
                          'INDEXBUFFER': GlirIndexBuffer,
                          }
    
    def parse(self, commands):
        """ Parse a list of commands.
        """
        
        for command in commands:
            cmd, id, args = command[0], command[1], command[2:]
            
            if cmd == 'CREATE':
                # Creating an object
                if args[0] is not None:
                    klass = self._classmap[args[0]]
                    self._objects[id] = klass()
                else:
                    self._invalid_objects.add(id)
            elif cmd == 'DELETE':
                # Deleteing an object
                ob = self._objects.get(id, None)
                if ob is not None:
                    ob.delete()
            else:
                # Doing somthing to an object
                ob = self._objects.get(id, None)
                if ob is None:
                    if id not in self._invalid_objects:
                        print('Cannot %s object %i because it does not exist' %
                              (cmd, id))
                    continue
                #
                if cmd == 'ACTIVATE':
                    ob.activate()
                elif cmd == 'DEACTIVATE':
                    ob.deactivate()
                elif cmd == 'SET_SIZE':
                    ob.set_size(*args)
                elif cmd == 'SET_DATA':
                    ob.set_data(*args)
                else:
                    print('Invalud GLIR command %r' % cmd)
                # SET_UNIFORM SET_ATTRIBUTE SET_SHADERS DRAW


## GLIR objects


class GlirObject(object):
    pass
    
    
class GlirBuffer(GlirObject):
    _target = None
    _usage = gl.GL_DYNAMIC_DRAW  # STATIC_DRAW, STREAM_DRAW or DYNAMIC_DRAW
    
    def __init__(self):
        self._handle = gl.glCreateBuffer()
        self._buffer_size = 0
        self._bufferSubDataOk = False
    
    def delete(self):
        gl.glDeleteBuffer(self._handle)
    
    def activate(self):
        gl.glBindBuffer(self._target, self._handle)
    
    def deactivate(self):
        pass  # Can only do this if Program uses GLIR too 
        # gl.glBindBuffer(self._target, 0)
    
    def set_size(self, nbytes):  # in bytes
        gl.glBindBuffer(self._target, self._handle)
        
        gl.glBufferData(self._target, nbytes, self._usage)
        self._buffer_size = nbytes
    
    def set_data(self, offset, data):
        gl.glBindBuffer(self._target, self._handle)
        
        nbytes = data.nbytes
        
        # Determine whether to check errors to try handling the ATI bug
        check_ati_bug = ((not self._bufferSubDataOk) and
                         (gl.current_backend is gl.desktop) and
                         sys.platform.startswith('win'))

        # flush any pending errors
        if check_ati_bug:
            gl.check_error('periodic check')
        
        try:
            gl.glBufferSubData(self._target, offset, data)
            if check_ati_bug:
                gl.check_error('glBufferSubData')
            self._bufferSubDataOk = True  # glBufferSubData seems to work
        except Exception:
            # This might be due to a driver error (seen on ATI), issue #64.
            # We try to detect this, and if we can use glBufferData instead
            if offset == 0 and nbytes == self._buffer_size:
                gl.glBufferData(self._target, data, self._usage)
                logger.debug("Using glBufferData instead of " +
                             "glBufferSubData (known ATI bug).")
            else:
                raise
    
    def exec_commands(self, commands):
        
        # todo: move this in the queue, before sending it of to a parser
        # Efficiency: purge all data commands that are followed by a resize
        data_commands = []
        other_commands = []
        for command in commands:
            if command[0] == 'resize':
                data_commands = []
            if command[0] == 'data':
                data_commands.append(command)
            else:
                other_commands.append(command)
        commands = other_commands + data_commands


class GlirVertexBuffer(GlirBuffer):
    _target = gl.GL_ARRAY_BUFFER
    

class GlirIndexBuffer(GlirBuffer):
    _target = gl.GL_ELEMENT_ARRAY_BUFFER,
