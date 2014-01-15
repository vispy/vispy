""" Called from vispy_ext.py to generate the GL API.
"""

import os
import sys
from vispy.gloo import gl

THISDIR = os.path.dirname(os.path.abspath(__file__))
DOCSDIR = os.path.join(THISDIR, '..')


def clean():
    fname = os.path.join(DOCSDIR, 'gl.rst')
    if os.path.isfile(fname):
        os.remove(fname)


def parse_api(ob):
    # Parse the namespace
    const_names = []
    func_names = []
    for name in dir(ob):
        if name.startswith('GL_'):
            const_names.append(name)
        elif name.startswith('gl'):
            func_names.append(name)
    return const_names, func_names


def main():

    lines = []

    # Get info
    gl_const_names, gl_func_names = parse_api(gl)
    glext_const_names, glext_func_names = parse_api(gl.ext)

    # Write title
    lines.append('OpenGL ES 2.0 API')
    lines.append('=' * len(lines[-1]))
    lines.append('')

    # Some info
    lines.append(
        'The ``vispy.gloo.gl`` namespace provides the OpenGL ES 2.0 API,')
    lines.append('Consisting of %i constants and %i functions ' %
                 (len(gl_const_names), len(gl_func_names)))
    lines.append('(with %i and %i more in the extensions) ' %
                 (len(glext_const_names), len(glext_func_names)))

    lines.append(
        'At this moment, the functions are taken from OpenGL.GL (provided by the PyOpenGL package).')
    lines.append('')

    # Write class header
    lines.append('**vispy.gloo.gl**\n')

    # Write constants and functions
    for name in sorted(gl_func_names):
        lines.append('  * %s()' % name)
    for name in sorted(gl_const_names):
        lines.append('  * %s' % name)

    # Write class header
    lines.append('**vispy.gloo.gl.ext**\n')

    # Write constants and functions
    for name in sorted(glext_func_names):
        lines.append('  * %s()' % name)
    for name in sorted(glext_const_names):
        lines.append('  * %s' % name)

    # Write file
    with open(os.path.join(DOCSDIR, 'gl.rst'), 'w') as f:
        f.write('\n'.join(lines))


if __name__ == '__main__':
    main()
