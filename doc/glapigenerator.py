""" Called from conf.py to generate the GL API.
"""

import os
import sys
from vispy import gl

THISDIR = os.path.dirname(os.path.abspath(__file__))

def main():
    
    # Parse the namespace
    const_names = []
    func_names = []
    for name in dir(gl):
        if name.startswith('GL_'):
            const_names.append(name)
        elif name.startswith('gl'):
            func_names.append(name)
    
    lines = []
    
    # Write title
    lines.append('OpenGL ES 2.0 API')
    lines.append('='*len(lines[-1]))
    lines.append('')
    
    # Some info
    lines.append('The ``vispy.gl`` namespace provides the OpenGL ES 2.0 API,')
    lines.append('Consisting of %i constants and %i functions.' %
                        (len(const_names), len(func_names)) )
    lines.append('At this moment, the functions are taken from OpenGL.GL (provided by the PyOpenGL package).')
    lines.append('')
    
    # Write class header
    lines.append('**vispy.gl**\n')
    
    # Write docstring
    for line in gl.__doc__.splitlines():
        line = line.strip()
        lines.append('    '+line)
    lines.append('')
    
    # Write constants and functions
    for name in sorted(const_names):
        lines.append('  * %s' % name)
    for name in sorted(func_names): 
        lines.append('  * %s()' % name)
    
    # Write file
    with open(os.path.join(THISDIR, 'gl.rst'), 'w') as f:
        f.write('\n'.join(lines))
    

if __name__ == '__main__':
    main()
