import pkgutil
import os

# make 'from module import *' work dynamically.
# otherwise we have to manually update the __all__ list.
# http://stackoverflow.com/questions/1057431/loading-all-modules-in-a-folder-in-python
__all__ = []

for module in os.listdir( os.path.dirname( __file__ ) ):
    name, extension = os.path.splitext( module )

    # don't import ourself
    if name == '__init__':
        continue

    # we can import .py, .pyc and .pyo file types
    extensions = [
        '.py',
        '.pyc',
        '.pyo'
        ]
    if extension not in extensions: 
        continue

    __all__.append( name )

