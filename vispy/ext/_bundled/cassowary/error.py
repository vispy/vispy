from __future__ import print_function, unicode_literals, absolute_import, division


class InternalError(Exception):
    pass


class ConstraintNotFound(Exception):
    pass


class RequiredFailure(Exception):
    pass
