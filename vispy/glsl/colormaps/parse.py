import os
import re


def get(filename):
    for path in ["..", "."]:
        filepath = os.path.join(path, filename)
        if os.path.exists(filepath):
            with open(filepath) as infile:
                code = infile.read()
                # comment = '#line 0 // Start of "%s"\n' % filename
                comment = '// --- start of "%s" ---\n' % filename
            return comment + code
    return '#error "%s" not found !\n' % filename

code = """
#include "colormap/colormaps.glsl"
"""

re_include = re.compile('\#include\s*"(?P<filename>[a-zA-Z0-9\-\.\/]+)"')

includes = []


def replace(match):
    filename = match.group("filename")
    if filename not in includes:
        includes.append(filename)
        text = get(filename)
        # lineno = code.count("\n",0,match.start())+1
        # text += '\n#line %d // End of "%s"' % (lineno, filename)
        text += '// --- end of "%s" ---\n' % filename
        return text
    return ''

while re.search(re_include, code):
    code = re.sub(re_include, replace, code)
print(code)
