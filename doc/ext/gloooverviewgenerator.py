""" Called from vispy_ext.py to generate the overview section of the
gloo docs. This section is simply added to gloo.__doc__.
"""

from vispy import gloo


def main():
    gloo.__doc__ += generate_overview_docs()


def clean():
    pass

EXCLUDE = ['ColorBuffer', 'DepthBuffer', 'StencilBuffer']
CLASSES = ['Program', 'VertexBuffer', 'IndexBuffer', 'Texture1D', 'Texture2D', 'Texture3D',
           'RenderBuffer', 'FrameBuffer']


def get_docs_for_class(klass):
    """ Get props and methods for a class.
    """

    # Prepare
    baseatts = dir(gloo.GLObject)
    functype = type(gloo.GLObject.delete)
    proptype = type(gloo.GLObject.id)
    props, funcs = set(), set()

    for att in sorted(dir(klass)):
        if att.startswith('_') or att.lower() != att:
            continue
        # Get ob and module name
        attob = getattr(klass, att)
        modulename = klass.__module__.split('.')[-1]
        # Get actual klass
        actualklass = klass
        while True:
            tmp = actualklass.__base__
            if att in dir(tmp):
                actualklass = tmp
            else:
                break
        if actualklass == klass:
            modulename = ''
        elif actualklass is gloo.GLObject:
            modulename = gloo.GLObject.__module__.split('.')[-1]
        # Append
        if isinstance(attob, functype):
            funcs.add(' :meth:`~%s.%s.%s`,' % (
                modulename, actualklass.__name__, att))
        elif isinstance(attob, proptype):
            props.add(' :attr:`~%s.%s.%s`,' % (
                modulename, actualklass.__name__, att))
    # Done
    return props, funcs


def generate_overview_docs():
    """ Generate the overview section for the gloo docs.
    """

    lines = []
    lines.append('Overview of most important GLOO classes')
    lines.append('=' * len(lines[-1]))
    klasseses = [(getattr(gloo, d),) for d in CLASSES]
    for klasses in klasseses:
        # Init line
        line = '*'
        for klass in klasses:
            line += ' :class:`%s`,' % klass.__name__
        line = line[:-1]
        # Get atts for these classes, sort by name, prop/func
        funcs, props = set(), set()
        for klass in klasses:
            props_, funcs_ = get_docs_for_class(klass)
            props.update(props_)
            funcs.update(funcs_)
        # Add props and funcs
        if props:
            line += '\n\n  * properties:'
            for item in sorted(props):
                line += item
        if funcs:
            line += '\n\n  * methods:'
            for item in sorted(funcs):
                line += item
            # Add line, strip last char
            lines.append(line[:-1])

    return '\n'.join(lines)


if __name__ == '__main__':
    print(generate_overview_docs())
