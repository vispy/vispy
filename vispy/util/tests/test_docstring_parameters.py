# TODO inspect for Cython (see sagenb.misc.sageinspect)
from __future__ import print_function

import inspect
import warnings
from vispy.testing import run_tests_if_main, requires_numpydoc
from vispy.util import _get_args


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

def check_parameters_match(func, cls=None):
    """Check docstring, return list of incorrect results."""
    from numpydoc.validate import validate
    name = _func_name(func, cls)
    skip = (not name.startswith('vispy.') or
            any(re.match(d, name) for d in docstring_ignores) or
            'deprecation_wrapped' in getattr(
                getattr(func, '__code__', None), 'co_name', ''))
    if skip:
        return list()
    if cls is not None:
        for subclass, ignores in subclass_name_ignores:
            if issubclass(cls, subclass) and name.split('.')[-1] in ignores:
                return list()
    incorrect = ['%s : %s : %s' % (name, err[0], err[1])
                 for err in validate(name)['errors']
                 if err[0] not in error_ignores and
                 (name.split('.')[-1], err[0]) not in error_ignores_specific]
    return incorrect


@requires_numpydoc()
def test_docstring_parameters():
    """Test module docsting formatting"""
    from numpydoc import docscrape
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
