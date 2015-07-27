# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
from weakref import WeakKeyDictionary

from ...ext.ordereddict import OrderedDict
from ...ext.six import string_types
from .compiler import Compiler


class ShaderObject(object):
    """ Base class for all objects that may be included in a GLSL program
    (Functions, Variables, Expressions).
    
    Shader objects have a *definition* that defines the object in GLSL, an 
    *expression* that is used to reference the object, and a set of 
    *dependencies* that must be declared before the object is used.
    
    Dependencies are tracked hierarchically such that changes to any object
    will be propagated up the dependency hierarchy to trigger a recompile.
    """

    @classmethod
    def create(self, obj, ref=None):
        """ Convert *obj* to a new ShaderObject. If the output is a Variable
        with no name, then set its name using *ref*. 
        """
        if isinstance(ref, Variable):
            ref = ref.name
        elif isinstance(ref, string_types) and ref.startswith('gl_'):
            # gl_ names not allowed for variables
            ref = ref[3:].lower()
        
        # Allow any type of object to be converted to ShaderObject if it
        # provides a magic method:
        if hasattr(obj, '_shader_object'):
            obj = obj._shader_object()
        
        if isinstance(obj, ShaderObject):
            if isinstance(obj, Variable) and obj.name is None:
                obj.name = ref
        elif isinstance(obj, string_types):
            obj = TextExpression(obj)
        else:
            obj = Variable(ref, obj)
            # Try prepending the name to indicate attribute, uniform, varying
            if obj.vtype and obj.vtype[0] in 'auv':
                obj.name = obj.vtype[0] + '_' + obj.name 
        
        return obj
    
    def __init__(self):
        # objects that must be declared before this object's definition.
        # {obj: refcount}
        self._deps = OrderedDict()  # OrderedDict for consistent code output
        
        # Objects that depend on this one will be informed of changes.
        self._dependents = WeakKeyDictionary()
    
    @property
    def name(self):
        """ The name of this shader object.
        """
        return None
        
    def definition(self, obj_names):
        """ Return the GLSL definition for this object. Use *obj_names* to
        determine the names of dependencies.
        """
        return None
    
    def expression(self, obj_names):
        """ Return the GLSL expression used to reference this object inline.
        """
        return obj_names[self]
    
    def dependencies(self, sort=False):
        """ Return all dependencies required to use this object. The last item 
        in the list is *self*.
        """
        alldeps = []
        if sort:
            def key(obj):
                # sort deps such that we get functions, variables, self.
                if not isinstance(obj, Variable):
                    return (0, 0)
                else:
                    return (1, obj.vtype)
            
            deps = sorted(self._deps, key=key)
        else:
            deps = self._deps
        
        for dep in deps:
            alldeps.extend(dep.dependencies(sort=sort))
        alldeps.append(self)
        return alldeps

    def static_names(self):
        """ Return a list of names that are declared in this object's 
        definition (not including the name of the object itself).
        
        These names will be reserved by the compiler when automatically 
        determining object names.
        """
        return []
    
    def _add_dep(self, dep):
        """ Increment the reference count for *dep*. If this is a new 
        dependency, then connect to its *changed* event.
        """
        if dep in self._deps:
            self._deps[dep] += 1
        else:
            self._deps[dep] = 1
            dep._dependents[self] = None

    def _remove_dep(self, dep):
        """ Decrement the reference count for *dep*. If the reference count 
        reaches 0, then the dependency is removed and its *changed* event is
        disconnected.
        """
        refcount = self._deps[dep]
        if refcount == 1:
            self._deps.pop(dep)
            dep._dependents.pop(self)
        else:
            self._deps[dep] -= 1

    def _dep_changed(self, dep, code_changed=False, value_changed=False):
        """ Called when a dependency's expression has changed.
        """
        self.changed(code_changed, value_changed)
            
    def changed(self, code_changed=False, value_changed=False):
        """Inform dependents that this shaderobject has changed.
        """
        for d in self._dependents:
            d._dep_changed(self, code_changed=code_changed,
                           value_changed=value_changed)
    
    def compile(self):
        """ Return a compilation of this object and its dependencies. 
        
        Note: this is mainly for debugging purposes; the names in this code
        are not guaranteed to match names in any other compilations. Use
        Compiler directly to ensure consistent naming across multiple objects. 
        """
        compiler = Compiler(obj=self)
        return compiler.compile()['obj']
    
    def __repr__(self):
        if self.name is not None:
            return '<%s "%s" at 0x%x>' % (self.__class__.__name__, 
                                          self.name, id(self))
        else:
            return '<%s at 0x%x>' % (self.__class__.__name__, id(self))


from .variable import Variable  # noqa
from .expression import TextExpression  # noqa
