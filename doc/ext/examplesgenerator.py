""" Called from vispy_conf.py to generate the examples for the docs from the
example Python files.
"""

from __future__ import print_function, division

import os
import sys
import shutil

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen  # Py3k


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_DIR = os.path.abspath(os.path.join(THIS_DIR, '..'))
EXAMPLES_DIR = os.path.abspath(os.path.join(DOC_DIR, '..', 'examples'))
OUTPUT_DIR = os.path.join(DOC_DIR, 'examples')


def clean():
    # Clear examples dir
    if os.path.isdir(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    # Clean examples file
    fname = os.path.join(DOC_DIR, 'examples.rst')
    if os.path.isfile(fname):
        os.remove(fname)


def main():

    clean()

    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    # Get examples and sort
    examples = list(get_example_filenames(EXAMPLES_DIR))
    examples.sort(key=lambda x: x[1])

    create_examples(examples)
    create_examples_list(examples)


def get_example_filenames(examples_dir):
    """ Yield (filename, name) elements for all examples. The examples
    are organized in directories, therefore the name can contain a
    forward slash.
    """
    for (dirpath, dirnames, filenames) in os.walk(examples_dir):
        for fname in filenames:
            if not fname.endswith('.py'):
                continue
            filename = os.path.join(dirpath, fname)
            name = filename[len(examples_dir):].lstrip('/\\')[:-3]
            name = name.replace('\\', '/')
            yield filename, name


def create_examples(examples):

    # Create doc file for each example
    for filename, name in examples:
        print('Writing example %s' % name)

        # Create title
        lines = []
        lines.append(name)
        lines.append('-' * len(lines[-1]))
        lines.append('')

        # Get source
        in_gallery = False
        doclines = []
        sourcelines = []
        with open(os.path.join(EXAMPLES_DIR, name + '.py')) as f:
            for line in f.readlines():
                line = line.rstrip()
                if line.startswith('# vispy:') and 'gallery' in line:
                    in_gallery = True
                if not doclines:
                    if line.startswith('"""'):
                        doclines.append(line.lstrip('" '))
                        sourcelines = []
                    else:
                        sourcelines.append('    ' + line)
                elif not sourcelines:
                    if '"""' in line:
                        sourcelines.append('    ' + line.partition('"""')[0])
                    else:
                        doclines.append(line)
                else:
                    sourcelines.append('    ' + line)

        # Add desciprion
        lines.extend(doclines)
        lines.append('')

        # Add source code
        lines.append('.. code-block:: python')
        lines.append('    ')
        lines.extend(sourcelines)
        lines.append('')

        # Write
        output_filename = os.path.join(OUTPUT_DIR, name + '.rst')
        output_dir = os.path.dirname(output_filename)
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        with open(output_filename, 'w') as f:
            f.write('\n'.join(lines))


def create_examples_list(examples):

    # Create TOC
    lines = []
    lines.append('List of examples')
    lines.append('=' * len(lines[-1]))
    lines.append('')

    # Add entry for each example that we know
    for _, name in examples:
        lines.append('* :doc:`examples/%s`' % name)

    # Write file
    with open(os.path.join(DOC_DIR, 'examples.rst'), 'w') as f:
        f.write('\n'.join(lines))


if __name__ == '__main__':
    main()
