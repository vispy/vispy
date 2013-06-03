""" Run tests using nose.

"""

import os
import sys
import nose

os.rename('__init__.py', '__init__.py.disabled')

try:
    result = nose.run()
finally:
    os.rename('__init__.py.disabled', '__init__.py')
