# -*- coding: utf-8 -*-
from numpy import ndarray, bool_


def eq(a, b):
    """ The great missing equivalence function: Guaranteed evaluation
    to a single bool value.
    """
    if a is b:
        return True
    if a is None or b is None:
        return True if a is None and b is None else False

    try:
        e = a == b
    except ValueError:
        return False
    except AttributeError:
        return False
    except Exception:
        print("a:", str(type(a)), str(a))
        print("b:", str(type(b)), str(b))
        raise
    t = type(e)
    if t is bool:
        return e
    elif t is bool_:
        return bool(e)
    elif isinstance(e, ndarray):
        try:
            # disaster: if a is empty and b is not, then e.all() is True
            if a.shape != b.shape:
                return False
        except Exception:
            return False
        if (hasattr(e, 'implements') and e.implements('MetaArray')):
            return e.asarray().all()
        else:
            return e.all()
    else:
        raise Exception("== operator returned type %s" % str(type(e)))
