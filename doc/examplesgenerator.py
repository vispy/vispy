""" Called from conf.py to generate the examples for the docs from the 
example Python files.
"""

import os
import sys

THISDIR = os.path.dirname(os.path.abspath(__file__))
EXAMPLESDIR = os.path.join(THISDIR, '..', 'examples')
OUTPUTDIR = os.path.join(THISDIR, 'examples')


def clean():
    # Clear examples dir
    if os.path.isdir(OUTPUTDIR):
        for fname in os.listdir(OUTPUTDIR):
            if fname.endswith('.rst'):
                os.remove(os.path.join(OUTPUTDIR, fname))
        os.rmdir(OUTPUTDIR)
    # Clean examples file
    fname = os.path.join(THISDIR, 'examples.rst')
    if os.path.isfile(fname):
        os.remove(fname)


def main():
    
    clean()
    
    if not os.path.isdir(OUTPUTDIR):
        os.mkdir(OUTPUTDIR)
    
    example_names = []
    
    # Create doc file for each example
    for fname in sorted(os.listdir(EXAMPLESDIR)):
        if not fname.endswith('.py'):
            continue
            
        # Get name and remember it
        name = fname[:-3]
        example_names.append(name)
        
        # Create title
        lines = []
        lines.append(name)
        lines.append('-'*len(name))
        lines.append('')
        
        # Get source
        doclines = []
        sourcelines = []
        with open(os.path.join(EXAMPLESDIR, fname)) as f:
            for line in f.readlines():
                line = line.rstrip()
                if not doclines:
                    if line.startswith('"""'):
                        doclines.append(line.lstrip('" '))
                elif not sourcelines:
                    if '"""' in line:
                        sourcelines.append('    ' + line.partition('"""')[0])
                    else:
                        doclines.append(line)
                else:
                    sourcelines.append('    ' + line)
        
        # Add desciprion and source code
        lines.extend(doclines)
        lines.append('')
        lines.append('.. code-block:: python')
        lines.append('    ')
        lines.extend(sourcelines)
        lines.append('')
        
        # Write
        with open(os.path.join(OUTPUTDIR, name+'.rst'), 'w') as f:
            f.write('\n'.join(lines))
    
    
    # Create TOC
    lines = []
    lines.append('Examples\n========\n')
    
    # Add entry for each example that we know
    for name in example_names:    
        lines.append('  * :doc:`examples/%s`' % name)
    
    # Write file
    with open(os.path.join(THISDIR, 'examples.rst'), 'w') as f:
        f.write('\n'.join(lines))


if __name__ == '__main__':
    main()

