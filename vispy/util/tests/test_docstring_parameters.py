# TODO inspect for Cython (see sagenb.misc.sageinspect)

import re
import inspect
import pytest

import vispy.scene.cameras.magnify
from vispy.testing import run_tests_if_main, requires_numpydoc


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


def _func_name(func, cls=None):
    """Get the name."""
    parts = []
    if cls is not None:
        module = inspect.getmodule(cls)
    else:
        module = inspect.getmodule(func)
    if module:
        parts.append(module.__name__)
    if cls is not None:
        parts.append(cls.__name__)
    parts.append(func.__name__)
    return '.'.join(parts)


# functions to ignore
docstring_ignores = [
    'vispy.scene.visuals',  # not parsed properly by this func, copies anyway
]
error_ignores = {
    # These we do not live by:
    'GL01',  # Docstring should start in the line immediately after the quotes
    'EX01', 'EX02',  # examples failed (we test them separately)
    'ES01',  # no extended summary
    'SA01',  # no see also
    'YD01',  # no yields section
    'SA04',  # no description in See Also
    'PR04',  # Parameter "shape (n_channels" has no type
    'RT02',  # The first line of the Returns section should contain only the type, unless multiple values are being returned  # noqa
    # XXX should also verify that | is used rather than , to separate params
    # XXX should maybe also restore the parameter-desc-length < 800 char check
}
error_ignores_specific = {}
subclass_name_ignores = (
    (vispy.scene.cameras.magnify.MagnifyCamera, {'MagnifyTransform', 'Magnify1DTransform'}),
)


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


@pytest.mark.xfail
@requires_numpydoc()
def test_docstring_parameters():
    """Test module docstring formatting."""
    from numpydoc import docscrape
    incorrect = []
    for name in public_modules:
        # Assert that by default we import all public names with `import vispy`
        # if name not in ('vispy'):
        #    extra = name.split('.')[1]
        #    assert hasattr(vispy, extra)
        with pytest.warns(None):  # traits warnings
            module = __import__(name, globals())
        for submod in name.split('.')[1:]:
            module = getattr(module, submod)
        classes = inspect.getmembers(module, inspect.isclass)
        for cname, cls in classes:
            if cname.startswith('_'):
                continue
            incorrect += check_parameters_match(cls)
            cdoc = docscrape.ClassDoc(cls)
            for method_name in cdoc.methods:
                method = getattr(cls, method_name)
                incorrect += check_parameters_match(method, cls=cls)
            if hasattr(cls, '__call__') and \
                    'of type object' not in str(cls.__call__):
                incorrect += check_parameters_match(cls.__call__, cls)
        functions = inspect.getmembers(module, inspect.isfunction)
        for fname, func in functions:
            if fname.startswith('_'):
                continue
            incorrect += check_parameters_match(func)
    incorrect = sorted(list(set(incorrect)))
    msg = '\n' + '\n'.join(incorrect)
    msg += '\n%d error%s' % (len(incorrect), 's' if len(incorrect) == 1 else '')
    if len(incorrect) > 0:
        raise AssertionError(msg)


run_tests_if_main()
