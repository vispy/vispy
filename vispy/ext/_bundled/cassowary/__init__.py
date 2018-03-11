from __future__ import print_function, unicode_literals, absolute_import

from .expression import Variable
from .error import RequiredFailure, ConstraintNotFound, InternalError
from .simplex_solver import SimplexSolver
from .utils import REQUIRED, STRONG, MEDIUM, WEAK

# Examples of valid version strings
# __version__ = '1.2.3.dev1'  # Development release 1
# __version__ = '1.2.3a1'     # Alpha Release 1
# __version__ = '1.2.3b1'     # Beta Release 1
# __version__ = '1.2.3rc1'    # RC Release 1
# __version__ = '1.2.3'       # Final Release
# __version__ = '1.2.3.post1' # Post Release 1

__version__ = '0.5.1'
