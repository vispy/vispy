# TODO inspect for Cython (see sagenb.misc.sageinspect)
from __future__ import print_function

from nose.plugins.skip import SkipTest
from os import path as op
import inspect
import warnings
import imp
from vispy.testing import run_tests_if_main

public_modules = [
    # the list of modules users need to access for all functionality
    'vispy',
    'vispy.color',
    'vispy.geometry',
    'vispy.gloo',
    'vispy.io',
    'vispy.plot',
    'vispy.scene',
    'vispy.util',
    'vispy.visuals',
]

docscrape_path = op.join(op.dirname(__file__), '..', '..', '..', 'doc', 'ext',
                         'docscrape.py')
if op.isfile(docscrape_path):
    docscrape = imp.load_source('docscrape', docscrape_path)
else:
    docscrape = None


def get_name(func):
    parts = []
    module = inspect.getmodule(func)
    if module:
        parts.append(module.__name__)
    if hasattr(func, 'im_class'):
        parts.append(func.im_class.__name__)
    parts.append(func.__name__)
    return '.'.join(parts)


# functions to ignore
_ignores = [
    'vispy.scene.visuals',  # not parsed properly by this func, copies anyway
]


def check_parameters_match(func, doc=None):
    """Helper to check docstring, returns list of incorrect results"""
    incorrect = []
    name_ = get_name(func)
    if not name_.startswith('vispy.'):
        return incorrect
    if inspect.isdatadescriptor(func):
        return incorrect
    args, varargs, varkw, defaults = inspect.getargspec(func)
    # drop self
    if len(args) > 0 and args[0] in ('self', 'cls'):
        args = args[1:]

    if doc is None:
        with warnings.catch_warnings(record=True) as w:
            doc = docscrape.FunctionDoc(func)
        if len(w):
            raise RuntimeError('Error for %s:\n%s' % (name_, w[0]))
    # check set
    param_names = [name for name, _, _ in doc['Parameters']]
    # clean up some docscrape output:
    param_names = [name.split(':')[0].strip('` ') for name in param_names]
    param_names = [name for name in param_names if '*' not in name]
    if len(param_names) != len(args):
        bad = str(sorted(list(set(param_names) - set(args)) +
                         list(set(args) - set(param_names))))
        if not any(d in name_ for d in _ignores):
            incorrect += [name_ + ' arg mismatch: ' + bad]
    else:
        for n1, n2 in zip(param_names, args):
            if n1 != n2:
                incorrect += [name_ + ' ' + n1 + ' != ' + n2]
    return incorrect


def test_docstring_parameters():
    """Test module docsting formatting"""
    if docscrape is None:
        raise SkipTest('This must be run from the vispy source directory')
    incorrect = []
    for name in public_modules:
        module = __import__(name, globals())
        for submod in name.split('.')[1:]:
            module = getattr(module, submod)
        classes = inspect.getmembers(module, inspect.isclass)
        for cname, cls in classes:
            if cname.startswith('_'):
                continue
            with warnings.catch_warnings(record=True) as w:
                cdoc = docscrape.ClassDoc(cls)
            if len(w):
                raise RuntimeError('Error for __init__ of %s in %s:\n%s'
                                   % (cls, name, w[0]))
            if hasattr(cls, '__init__'):
                incorrect += check_parameters_match(cls.__init__, cdoc)
            for method_name in cdoc.methods:
                method = getattr(cls, method_name)
                # skip classes that are added as attributes of classes
                if (inspect.ismethod(method) or inspect.isfunction(method)):
                    incorrect += check_parameters_match(method)
            if hasattr(cls, '__call__'):
                incorrect += check_parameters_match(cls.__call__)
        functions = inspect.getmembers(module, inspect.isfunction)
        for fname, func in functions:
            if fname.startswith('_'):
                continue
            incorrect += check_parameters_match(func)
    msg = '\n' + '\n'.join(sorted(list(set(incorrect))))
    if len(incorrect) > 0:
        msg += '\n\n%s docstring violations found' % msg.count('\n')
        raise AssertionError(msg)


run_tests_if_main()
