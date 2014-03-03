"""

The visualization
-----------------

We create a visualization where the screen is divided in 4 quadrants,
and each quadrant is painted a different color (black, red, green,
blue). The painting is done for 50% using attribute data, and 50%
using a texture. The end result should be fully saturated colors.

Remember: the bottom left is (-1, -1) and the first quadrant. 

"""
import sys
import time

import numpy as np

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal
from numpy.testing import assert_almost_equal
from vispy.app.backends import requires_non_glut

from vispy.gloo import gl
from vispy import app


# All these tests require a working backend. GLUT is not an option,
# since there is no safe way to terminate the mainloop.
# requires_non_glut works if there is a backend other then GLUT available.

# Whether to sleep in order to show the result. True when running as script
SLEEP = False


@requires_non_glut()
def test_functionality_desktop():
    """ Test that desktop GL backend functions appropriately. """
    _test_functonality('desktop')


@requires_non_glut()
@gl._requires_pyopengl()
def test_functionality_pypengl():
    """ Test that pyopengl GL backend functions appropriately. """
    _test_functonality('pyopengl')


@requires_non_glut()
def test_functionality_angle():
    """ Test that angle GL backend functions appropriately. """
    if True:
        raise SkipTest('Skip Angle functionality test for now.')
    if sys.platform.startswith('win'):
        raise SkipTest('Can only test angle functionality on Windows.')

    _test_functonality('angle')


def _test_functonality(backend):
    """ Create app and canvas so we have a context. Then run tests.
    """

    # use the backend
    gl.use(backend)

    # Create app and canvas to get an OpenGL context
    app.create()
    c = app.Canvas()
    c.show()
    app.process_events(); app.process_events()

    try:
        # General tests. Some variables are set though
        _test_setting_parameters(c)
        _test_enabling_disabling()
        _test_setting_stuff()
        _test_object_creation_and_deletion()
        
        # Prepare
        _test_prepare_vis()
        app.process_events(); app.process_events()
        
        # Draw 1
        _draw1()
        gl.glFinish()
        app.process_events(); app.process_events()
        _test_result()
        c.swap_buffers()
        app.process_events(); app.process_events()
        if SLEEP:  time.sleep(1.0)
        
        # Draw 2
        _draw2()
        gl.glFinish()
        app.process_events(); app.process_events()
        _test_result()
        c.swap_buffers()
        app.process_events(); app.process_events()
        if SLEEP:  time.sleep(1.0)
        
        # Draw 3
        _draw3()
        gl.glFinish()
        app.process_events(); app.process_events()
        _test_result()
        c.swap_buffers()
        app.process_events(); app.process_events()
        if SLEEP:  time.sleep(1.0)
        
    
    finally:
        c.close()


## Create CPU data

# Create vertex and fragments shader. They are designed to that all
# OpenGL func can be tested, i.e. all types of uniforms are present.
# Most variables are nullified however, but we must make sure we do this
# in a way that the compiler won't optimize out :)
VERT = """
attribute vec2 a_2;
attribute vec3 a_3;
attribute vec4 a_4;

uniform float u_f1;
uniform vec2 u_f2;
uniform vec3 u_f3;
uniform vec4 u_f4;

uniform int u_i1;
uniform ivec2 u_i2;
uniform ivec3 u_i3;
uniform ivec4 u_i4;

uniform mat2 u_m2;
uniform mat3 u_m3;
uniform mat4 u_m4;

varying vec2 v_2;  // tex coords
varying vec4 v_4;  // attr colors

void main()
{   
    float zero = float(u_i1);
    
    // Combine int with float uniforms (i.e. ints are "used")
    float u1 = u_f1 + float(u_i1);
    vec2 u2 = u_f2 + vec2(u_i2);
    vec3 u3 = u_f3 + vec3(u_i3);
    vec4 u4 = u_f4 + vec4(u_i4);
    
    // Set varyings (use every 2D and 4D variable, and u1)
    v_2 = a_2 + zero*u_m2 * a_2 * u2 * u1;
    v_4 = u_m4 * a_4 * u4;
    
    // Set position (use 3D variables)
    gl_Position = vec4(u_m3* a_3* u3, 1.0);
}
"""

FRAG = """

uniform sampler2D s_1;
uniform int u_i1;
varying vec2 v_2;  // rex coords
varying vec4 v_4;  // attr colors

void main()
{   
    float zero = float(u_i1);
    gl_FragColor = (texture2D(s_1, v_2) + v_4);
}
"""

# Color texture
texquad = 5
im1 = np.zeros((texquad*2, texquad*2, 3), np.uint8)
im1[texquad:, :texquad, 0] = 128
im1[texquad:, texquad:, 1] = 128
im1[:texquad, texquad:, 2] = 128

# Grayscale texture (uploaded but not used)
im2 = im1[:,:,0]  # A non-contiguous view
assert im2.flags['C_CONTIGUOUS'] == False

# Vertex Buffers

# Create coordinates for upper left quad
quad = np.array([[0, 0, 0], [-1, 0, 0], [-1, -1, 0], [0, 0, 0], [-1, -1, 0], [0, -1, 0]], np.float32)
N = quad.shape[0] * 4

# buf3 contains coordinates in device coordinates for four quadrants
buf3 = np.row_stack([quad + (0, 0, 0), quad + (0, 1, 0),
                     quad + (1, 1, 0), quad + (1, 0, 0)]).astype(np.float32)

# buf2 is texture coords. Note that this is a view on buf2
buf2 = ((buf3+1.0)*0.5)[:,:2]    # not C-contiguous
assert buf2.flags['C_CONTIGUOUS'] == False

# Array of colors
buf4 = np.zeros((N, 4), np.float32)
buf4[6:12, 0] = 0.5
buf4[12:18, 1] = 0.5
buf4[18:24, 2] = 0.5
buf4[:, 3] = 1.0  # alpha


# Element buffer
elements = np.arange(N, dtype=np.uint8)
helements = None  # the OpenGL object ref


## The actual tests

def _test_setting_parameters(c):
    # Set some parameters and get result
    w, h = c.size
    gl.glViewport(0, 0, w, h)
    #
    clr = 0.0, 0.0, 0.0, 1.0  # 1.0, 0.1, 0.2, 0.7
    gl.glClearColor(*clr)
    assert_almost_equal(gl.glGetParameter(gl.GL_COLOR_CLEAR_VALUE), clr)
    #
    gl.glCullFace(gl.GL_FRONT)
    assert_equal(gl.glGetParameter(gl.GL_CULL_FACE_MODE), gl.GL_FRONT)
    gl.glCullFace(gl.GL_BACK)
    assert_equal(gl.glGetParameter(gl.GL_CULL_FACE_MODE), gl.GL_BACK)
    #
    gl.glDepthFunc(gl.GL_NOTEQUAL)
    assert_equal(gl.glGetParameter(gl.GL_DEPTH_FUNC), gl.GL_NOTEQUAL)
    #
    val = 0.2, 0.3
    gl.glDepthRange(*val)
    assert_almost_equal(gl.glGetParameter(gl.GL_DEPTH_RANGE), val)


def _test_enabling_disabling():
    # Enabling/disabling
    gl.glEnable(gl.GL_DEPTH_TEST)
    assert_equal(gl.glIsEnabled(gl.GL_DEPTH_TEST), True)
    assert_equal(gl.glGetParameter(gl.GL_DEPTH_TEST), 1)
    gl.glDisable(gl.GL_DEPTH_TEST)
    assert_equal(gl.glIsEnabled(gl.GL_DEPTH_TEST), False)
    assert_equal(gl.glGetParameter(gl.GL_DEPTH_TEST), 0)
    #
    gl.glEnable(gl.GL_BLEND)
    assert_equal(gl.glIsEnabled(gl.GL_BLEND), True)
    assert_equal(gl.glGetParameter(gl.GL_BLEND), 1)
    gl.glDisable(gl.GL_BLEND)
    assert_equal(gl.glIsEnabled(gl.GL_BLEND), False)
    assert_equal(gl.glGetParameter(gl.GL_BLEND), 0)


def _test_setting_stuff():
    # Just do some actions
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)


def _test_object_creation_and_deletion():

    # Stuff that is originally glGenX

    # Create/delete texture
    assert_equal(gl.glIsTexture(1), False)
    handle = gl.glCreateTexture()
    gl.glBindTexture(gl.GL_TEXTURE_2D, handle)
    assert_equal(gl.glIsTexture(handle), True)
    gl.glDeleteTexture(handle)
    assert_equal(gl.glIsTexture(handle), False)

    # Create/delete buffer
    assert_equal(gl.glIsBuffer(1), False)
    handle = gl.glCreateBuffer()
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, handle)
    assert_equal(gl.glIsBuffer(handle), True)
    gl.glDeleteBuffer(handle)
    assert_equal(gl.glIsBuffer(handle), False)

    # Create/delete framebuffer
    assert_equal(gl.glIsFramebuffer(1), False)
    handle = gl.glCreateFramebuffer()
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, handle)
    assert_equal(gl.glIsFramebuffer(handle), True)
    gl.glDeleteFramebuffer(handle)
    assert_equal(gl.glIsFramebuffer(handle), False)

    # Create/delete renderbuffer
    assert_equal(gl.glIsRenderbuffer(1), False)
    handle = gl.glCreateRenderbuffer()
    gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, handle)
    assert_equal(gl.glIsRenderbuffer(handle), True)
    gl.glDeleteRenderbuffer(handle)
    assert_equal(gl.glIsRenderbuffer(handle), False)

    # Stuff that is originally called glCreate

    # Create/delete program
    assert_equal(gl.glIsProgram(1), False)
    handle = gl.glCreateProgram()
    assert_equal(gl.glIsProgram(handle), True)
    gl.glDeleteProgram(handle)
    assert_equal(gl.glIsProgram(handle), False)

    # Create/delete shader
    assert_equal(gl.glIsShader(1), False)
    handle = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    assert_equal(gl.glIsShader(handle), True)
    gl.glDeleteShader(handle)
    assert_equal(gl.glIsShader(handle), False)
    
    # Check if all is ok
    assert_equal(gl.glGetError(), 0)


def _test_prepare_vis():
    
    # --- program and shaders
    
    # Create program and shaders
    hprog = gl.glCreateProgram()
    hvert = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    hfrag = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
    
    # Compile source code
    gl.glShaderSource_compat(hvert, VERT)
    gl.glShaderSource_compat(hfrag, FRAG)
    gl.glCompileShader(hvert)
    gl.glCompileShader(hfrag)
    
    # Check
    assert_equal(gl.glGetShaderInfoLog(hvert), '')
    assert_equal(gl.glGetShaderInfoLog(hfrag), '')
    assert_equal(gl.glGetShaderParameter(hvert, gl.GL_COMPILE_STATUS), 1)
    assert_equal(gl.glGetShaderParameter(hfrag, gl.GL_COMPILE_STATUS), 1)
    
    # Attach and link
    gl.glAttachShader(hprog, hvert)
    gl.glAttachShader(hprog, hfrag)
    gl.glLinkProgram(hprog)
    
    # Check
    assert_equal(gl.glGetProgramInfoLog(hprog), '')
    assert_equal(gl.glGetProgramParameter(hprog, gl.GL_LINK_STATUS), 1)
    
    # Use it!
    gl.glUseProgram(hprog)
    
    # Check if all is ok
    assert_equal(gl.glGetError(), 0)
    
    
    # --- get information on attributes and uniforms
    
    # Count attribbutes and uniforms
    natt = gl.glGetProgramParameter(hprog, gl.GL_ACTIVE_ATTRIBUTES)
    nuni = gl.glGetProgramParameter(hprog, gl.GL_ACTIVE_UNIFORMS)
    assert_equal(natt, 3)
    assert_equal(nuni, 4+4+3+1)
    
    # Get names
    names = {}
    for i in range(natt):
        name, count, type = gl.glGetActiveAttrib(hprog, i)
        names[name] = type
        assert_equal(count, 1)
    for i in range(nuni):
        name, count, type = gl.glGetActiveUniform(hprog, i)
        names[name] = type
        assert_equal(count, 1)
    
    # Check
    assert_equal(names['a_2'], gl.GL_FLOAT_VEC2)
    assert_equal(names['a_3'], gl.GL_FLOAT_VEC3)
    assert_equal(names['a_4'], gl.GL_FLOAT_VEC4)
    assert_equal(names['s_1'], gl.GL_SAMPLER_2D)
    #
    for i, type in enumerate([gl.GL_FLOAT, gl.GL_FLOAT_VEC2, 
                              gl.GL_FLOAT_VEC3, gl.GL_FLOAT_VEC4]):
        assert_equal(names['u_f%i' % (i+1)], type)
    for i, type in enumerate([gl.GL_INT, gl.GL_INT_VEC2, 
                              gl.GL_INT_VEC3, gl.GL_INT_VEC4]):
        assert_equal(names['u_i%i' % (i+1)], type)
    for i, type in enumerate([gl.GL_FLOAT_MAT2, gl.GL_FLOAT_MAT3, 
                              gl.GL_FLOAT_MAT4]):
        assert_equal(names['u_m%i' % (i+2)], type)
    
    # Check if all is ok
    assert_equal(gl.glGetError(), 0)
    
    
    # --- texture
    
    # Create, bind, activate
    htex = gl.glCreateTexture()
    gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, htex)
    
    # Allocate data and upload
    # This data is luminance and not C-contiguous
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_LUMINANCE, gl.GL_LUMINANCE, 
                    gl.GL_UNSIGNED_BYTE, im2.shape[:2])
    gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, gl.GL_LUMINANCE,
                       gl.GL_UNSIGNED_BYTE, im2)
    
    # Set texture parameters
    T = gl.GL_TEXTURE_2D
    gl.glTexParameteri(T, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(T, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    
    # Re-allocate data and upload 
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, gl.GL_RGB, 
                    gl.GL_UNSIGNED_BYTE, im1.shape[:2])
    gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, gl.GL_RGB,
                       gl.GL_UNSIGNED_BYTE, im1)
    
    # Attach!
    loc = gl.glGetUniformLocation(hprog, 's_1')
    unit = 0
    gl.glActiveTexture(gl.GL_TEXTURE0+unit)
    gl.glUniform1i(loc, unit) 
    
    # Check if all is ok
    assert_equal(gl.glGetError(), 0)
    
    
    # --- buffer vec2 (contiguous VBO)
    
    # Create buffer
    hbuf2 = gl.glCreateBuffer()
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, hbuf2)

    # Allocate and set data
    gl.glBufferData(gl.GL_ARRAY_BUFFER, buf2.nbytes, gl.GL_DYNAMIC_DRAW)
    gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, buf2)
    
    # Attach!
    loc = gl.glGetAttribLocation(hprog, 'a_2')
    gl.glEnableVertexAttribArray(loc)
    gl.glVertexAttribPointer(loc, 2, gl.GL_FLOAT, False, 2*4, 0)
    
    # Check if all is ok
    assert_equal(gl.glGetError(), 0)
    
    
    # --- buffer vec3 (non-contiguous VBO)
    
    # Create buffer
    hbuf3 = gl.glCreateBuffer()
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, hbuf3)

    # Allocate and set data
    gl.glBufferData(gl.GL_ARRAY_BUFFER, buf3.nbytes, gl.GL_DYNAMIC_DRAW)
    gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, buf3)
    
    # Attach!
    loc = gl.glGetAttribLocation(hprog, 'a_3')
    gl.glEnableVertexAttribArray(loc)
    gl.glVertexAttribPointer(loc, 3, gl.GL_FLOAT, False, 3*4, 0)
    
    # Check if all is ok
    assert_equal(gl.glGetError(), 0)
    
    
    # --- buffer vec4 (client vertex data)
    
    # Select no FBO
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
    
    # Attach!
    loc = gl.glGetAttribLocation(hprog, 'a_4')
    gl.glEnableVertexAttribArray(loc)
    gl.glVertexAttribPointer(loc, 4, gl.GL_FLOAT, False, 4*4, buf4)
    
    # Check if all is ok
    assert_equal(gl.glGetError(), 0)
    
    
    # --- element buffer
    
    # Create buffer
    global helements
    helements = gl.glCreateBuffer()
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, helements)

    # Allocate and set data
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, elements, gl.GL_DYNAMIC_DRAW)
#     gl.glBufferSubData(gl.GL_ELEMENT_ARRAY_BUFFER, 0, elements)
    
    # Turn off
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)
    
    # Check if all is ok
    assert_equal(gl.glGetError(), 0)
    
    
    # --- uniforms
    
    # Set integer uniforms to 0
    # We set them twice just to touch both i and iv functions
    for i, fun1, fun2 in [(1, gl.glUniform1i, gl.glUniform1iv),
                          (2, gl.glUniform2i, gl.glUniform2iv),
                          (3, gl.glUniform3i, gl.glUniform3iv),
                          (4, gl.glUniform4i, gl.glUniform4iv)]:
        name = 'u_i%i' % i
        value = [0] * i
        loc = gl.glGetUniformLocation(hprog, name)
        fun1(loc, *value)  # e.g. glUniform4i
        fun2(loc, 1, value)  # e.g. glUniform4iv

    # Set float uniforms to 1.0
    # We set them twice just to touch both i and iv functions
    for i, fun1, fun2 in [(1, gl.glUniform1f, gl.glUniform1fv),
                          (2, gl.glUniform2f, gl.glUniform2fv),
                          (3, gl.glUniform3f, gl.glUniform3fv),
                          (4, gl.glUniform4f, gl.glUniform4fv)]:
        name = 'u_f%i' % i
        value = [1.0] * i
        loc = gl.glGetUniformLocation(hprog, name)
        fun1(loc, *value)  # e.g. glUniform4f
        fun2(loc, 1, value)  # e.g. glUniform4fv
    
    # Set matrix uniforms
    loc = gl.glGetUniformLocation(hprog, 'u_m2')
    gl.glUniformMatrix2fv(loc, 1, False, np.eye(2, dtype='float32'))
    loc = gl.glGetUniformLocation(hprog, 'u_m3')
    gl.glUniformMatrix3fv(loc, 1, False, np.eye(3, dtype='float32'))
    loc = gl.glGetUniformLocation(hprog, 'u_m4')
    gl.glUniformMatrix4fv(loc, 1, False, np.eye(4, dtype='float32'))
    
    # Check if all is ok
    assert_equal(gl.glGetError(), 0)
    
    
    # --- flush and finish
    
    # Not really necessary, but we want to touch the functions
    gl.glFlush()
    gl.glFinish()


def _draw1():
    # Draw using arrays
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, N)


def _draw2():
    global helements
    # Draw using elements via buffer
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, helements)
    gl.glDrawElements(gl.GL_TRIANGLES, elements.size, gl.GL_UNSIGNED_BYTE, 0)
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)


def _draw3():
    # Draw using elements via numpy array
    gl.glDrawElements(gl.GL_TRIANGLES, elements.size, gl.GL_UNSIGNED_BYTE, elements)
    

def _test_result():
    x, y, w, h = gl.glGetParameter(gl.GL_VIEWPORT)
    data = gl.glReadPixels(x, y, w, h, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
    im = np.frombuffer(data, np.uint8)
    im.shape = h, w, 3
    
    # Get center pixel from each quadrant
    pix1 = tuple(im[int(1*h/4), int(1*w/4)])
    pix2 = tuple(im[int(3*h/4), int(1*w/4)])
    pix3 = tuple(im[int(3*h/4), int(3*w/4)])
    pix4 = tuple(im[int(1*h/4), int(3*w/4)])
    
    # Test their value
    assert_equal(pix1, (0,0,0))
    assert_equal(pix2, (255,0,0))
    assert_equal(pix3, (0,255,0))
    assert_equal(pix4, (0,0,255))
    #print(pix1, pix2, pix3, pix4)


if __name__ == '__main__':
    SLEEP = True
    test_functionality_desktop()
    test_functionality_pypengl()
