import os
from . import logger


def fix_osmesa_gl_lib():
    """
    When using OSMesa, the gl functions (from libGL) are included
    in libOSMesa.so. This function modifies the VISPY_GL_LIB env variable
    so gl2 picks up libOSMesa.so as the OpenGL library.

    This modification must be done before vispy.gloo is imported for the
    first time.
    """
    if 'VISPY_GL_LIB' in os.environ:
        logger.warning('VISPY_GL_LIB is ignored when using OSMesa. Use '
                       'OSMESA_LIBRARY instead.')
    os.environ['VISPY_GL_LIB'] = os.getenv('OSMESA_LIBRARY', 'libOSMesa.so')
