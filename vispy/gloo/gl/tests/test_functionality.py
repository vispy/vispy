""" Test to verify the functionality of the OpenGL backends. This test
sets up a real visualization with shaders and all. This tests setting
source code, setting texture and buffer data, and we touch many other
functions of the API too. The end result is an image with four colored
quads. The result is tested for pixel color.

The visualization
-----------------

We create a visualization where the screen is divided in 4 quadrants,
and each quadrant is drawn a different color (black, red, green,
blue). The drawing is done for 50% using attribute data, and 50%
using a texture. The end result should be fully saturated colors.

Remember: the bottom left is (-1, -1) and the first quadrant.
"""
import sys

import numpy as np

from vispy.app import Canvas
from vispy.testing import (requires_application, requires_pyopengl, SkipTest,
                           run_tests_if_main, assert_equal, assert_true)

from vispy.gloo import gl

# All these tests require a working backend.


## High level tests

def teardown_module():
    gl.use_gl()  # Reset to default


@requires_application()
def test_functionality_desktop():
    """ Test desktop GL backend for full functionality. """
    _test_functionality('gl2')


@requires_application()
def test_functionality_proxy():
    """ Test GL proxy class for full functionality. """
    # By using debug mode, we are using the proxy class
    _test_functionality('gl2 debug')


@requires_application()
@requires_pyopengl()
def test_functionality_pyopengl():
    """ Test pyopengl GL backend for full functionality. """
    _test_functionality('pyopengl2')


@requires_application()
def test_functionality_es2():
    """ Test es2 GL backend for full functionality. """
    if True:
        raise SkipTest('Skip es2 functionality test for now.')
    if not sys.platform.startswith('win'):
        raise SkipTest('Can only test es2 functionality on Windows.')
    _test_functionality('es2')


def _clear_screen():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    gl.glFinish()


def _test_functionality(backend):
    """ Create app and canvas so we have a context. Then run tests.
    """
    # use the backend
    gl.use_gl(backend)
    
    with Canvas() as canvas:
        _clear_screen()
        
        # Prepare
        w, h = canvas.size
        gl.glViewport(0, 0, w, h)
        gl.glScissor(0, 0, w, h)  # touch
        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        
        # Setup visualization, ensure to do it in a draw event
        objects = _prepare_vis()
        _clear_screen()
        _draw1()
        _clear_screen()
        _draw2()
        _clear_screen()
        _draw3()

        # Clean up
        for delete_func, handle in objects:
            delete_func(handle)
        gl.glFinish()


## Create CPU data

# Create vertex and fragments shader. They are designed to that all
# OpenGL func can be tested, i.e. all types of uniforms are present.
# Most variables are nullified however, but we must make sure we do this
# in a way that the compiler won't optimize out :)
VERT = """
#version 120

attribute float a_1;
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
    v_2 = a_1 * a_2 + zero*u_m2 * a_2 * u2 * u1;
    v_4 = u_m4 * a_4 * u4;
    
    // Set position (use 3D variables)
    gl_Position = vec4(u_m3* a_3* u3, 1.0);
}
"""

FRAG = """
#version 120

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
im2 = im1[:, :, 0]  # A non-contiguous view
assert im2.flags['C_CONTIGUOUS'] is False

# Vertex Buffers

# Create coordinates for upper left quad
quad = np.array([[0, 0, 0], [-1, 0, 0], [-1, -1, 0], 
                 [0, 0, 0], [-1, -1, 0], [0, -1, 0]], np.float32)
N = quad.shape[0] * 4

# buf3 contains coordinates in device coordinates for four quadrants
buf3 = np.row_stack([quad + (0, 0, 0), quad + (0, 1, 0),
                     quad + (1, 1, 0), quad + (1, 0, 0)]).astype(np.float32)

# buf2 is texture coords. Note that this is a view on buf2
buf2 = ((buf3+1.0)*0.5)[:, :2]   # not C-contiguous
assert buf2.flags['C_CONTIGUOUS'] is False

# Array of colors
buf4 = np.zeros((N, 5), np.float32)
buf4[6:12, 0] = 0.5
buf4[12:18, 1] = 0.5
buf4[18:24, 2] = 0.5
buf4[:, 3] = 1.0  # alpha
buf4 = buf4[:, :4]  # make non-contiguous

# Element buffer
# elements = np.arange(N, dtype=np.uint8)  # C-contiguous
elements = np.arange(0, N, 0.5).astype(np.uint8)[::2]  # not C-contiguous
helements = None  # the OpenGL object ref


## The GL calls

def _prepare_vis():
    
    objects = []
    
    # --- program and shaders
    
    # Create program and shaders
    hprog = gl.glCreateProgram()
    hvert = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    hfrag = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
    objects.append((gl.glDeleteProgram, hprog))
    objects.append((gl.glDeleteShader, hvert))
    objects.append((gl.glDeleteShader, hfrag))
    
    # Compile source code
    gl.glShaderSource(hvert, VERT)
    gl.glShaderSource(hfrag, FRAG)
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
    # touch glDetachShader
    gl.glDetachShader(hprog, hvert)
    gl.glAttachShader(hprog, hvert)

    # Bind all attributes - we could let this occur automatically, but some
    # implementations bind an attribute to index 0, which has the unfortunate
    # property of being unable to be modified.
    gl.glBindAttribLocation(hprog, 1, 'a_1')
    gl.glBindAttribLocation(hprog, 2, 'a_2')
    gl.glBindAttribLocation(hprog, 3, 'a_3')
    gl.glBindAttribLocation(hprog, 4, 'a_4')

    gl.glLinkProgram(hprog)
    
    # Test that indeed these shaders are attached
    attached_shaders = gl.glGetAttachedShaders(hprog)
    assert_equal(set(attached_shaders), set([hvert, hfrag]))
    
    # Check
    assert_equal(gl.glGetProgramInfoLog(hprog), '')
    assert_equal(gl.glGetProgramParameter(hprog, gl.GL_LINK_STATUS), 1)
    gl.glValidateProgram(hprog)
    assert_equal(gl.glGetProgramParameter(hprog, gl.GL_VALIDATE_STATUS), 1)
    
    # Use it!
    gl.glUseProgram(hprog)
    
    # Check if all is ok
    assert_equal(gl.glGetError(), 0)
    
    # Check source
    vert_source = gl.glGetShaderSource(hvert)
    assert_true('attribute vec2 a_2;' in vert_source)
    
    # --- get information on attributes and uniforms
    
    # Count attributes and uniforms
    natt = gl.glGetProgramParameter(hprog, gl.GL_ACTIVE_ATTRIBUTES)
    nuni = gl.glGetProgramParameter(hprog, gl.GL_ACTIVE_UNIFORMS)
    assert_equal(natt, 4)
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
    assert_equal(names['a_1'], gl.GL_FLOAT)
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
    objects.append((gl.glDeleteTexture, htex))
    gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, htex)
    
    # Allocate data and upload
    # This data is luminance and not C-contiguous
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_LUMINANCE, gl.GL_LUMINANCE, 
                    gl.GL_UNSIGNED_BYTE, im2)  # touch
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_LUMINANCE, gl.GL_LUMINANCE, 
                    gl.GL_UNSIGNED_BYTE, im2.shape[:2])
    gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, gl.GL_LUMINANCE,
                       gl.GL_UNSIGNED_BYTE, im2)
    
    # Set texture parameters (use f and i to touch both)
    T = gl.GL_TEXTURE_2D
    gl.glTexParameterf(T, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
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
    
    # Mipmaps (just to touch this function)
    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
    
    # Check min filter (touch getTextParameter)
    minfilt = gl.glGetTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER)
    assert_equal(minfilt, gl.GL_LINEAR)
    
    # Check if all is ok
    assert_equal(gl.glGetError(), 0)
    
    # --- buffer vec2 (contiguous VBO)
    
    # Create buffer
    hbuf2 = gl.glCreateBuffer()
    objects.append((gl.glDeleteBuffer, hbuf2))
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, hbuf2)

    # Allocate and set data
    gl.glBufferData(gl.GL_ARRAY_BUFFER, buf2.nbytes, gl.GL_DYNAMIC_DRAW)
    gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, buf2)
    
    # Attach!
    loc = gl.glGetAttribLocation(hprog, 'a_2')
    gl.glDisableVertexAttribArray(loc)  # touch
    gl.glEnableVertexAttribArray(loc)
    gl.glVertexAttribPointer(loc, 2, gl.GL_FLOAT, False, 2*4, 0)
    
    # Check (touch glGetBufferParameter, glGetVertexAttrib and
    # glGetVertexAttribOffset)
    size = gl.glGetBufferParameter(gl.GL_ARRAY_BUFFER, gl.GL_BUFFER_SIZE)
    assert_equal(size, buf2.nbytes)
    stride = gl.glGetVertexAttrib(loc, gl.GL_VERTEX_ATTRIB_ARRAY_STRIDE)
    assert_equal(stride, 2*4)
    offset = gl.glGetVertexAttribOffset(loc, gl.GL_VERTEX_ATTRIB_ARRAY_POINTER)
    assert_equal(offset, 0)
    
    # Check if all is ok
    assert_equal(gl.glGetError(), 0)
    
    # --- buffer vec3 (non-contiguous VBO)
    
    # Create buffer
    hbuf3 = gl.glCreateBuffer()
    objects.append((gl.glDeleteBuffer, hbuf3))
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
    objects.append((gl.glDeleteBuffer, helements))
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, helements)

    # Allocate and set data
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, elements, gl.GL_DYNAMIC_DRAW)
    gl.glBufferSubData(gl.GL_ELEMENT_ARRAY_BUFFER, 0, elements)
    
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
    m = np.eye(5, dtype='float32')
    loc = gl.glGetUniformLocation(hprog, 'u_m2')
    gl.glUniformMatrix2fv(loc, 1, False, m[:2, :2])
    #
    loc = gl.glGetUniformLocation(hprog, 'u_m3')
    m = np.eye(3, dtype='float32')
    gl.glUniformMatrix3fv(loc, 1, False, m[:3, :3])
    #
    loc = gl.glGetUniformLocation(hprog, 'u_m4')
    m = np.eye(4, dtype='float32')
    gl.glUniformMatrix4fv(loc, 1, False, m[:4, :4])
    
    # Check some uniforms
    loc = gl.glGetUniformLocation(hprog, 'u_i1')
    assert_equal(gl.glGetUniform(hprog, loc), 0)
    loc = gl.glGetUniformLocation(hprog, 'u_i2')
    assert_equal(gl.glGetUniform(hprog, loc), (0, 0))
    loc = gl.glGetUniformLocation(hprog, 'u_f2')
    assert_equal(gl.glGetUniform(hprog, loc), (1.0, 1.0))
    
    # Check if all is ok
    assert_equal(gl.glGetError(), 0)
    
    # --- attributes 
    
    # Constant values for attributes. We do not even use this ...
    loc = gl.glGetAttribLocation(hprog, 'a_1')
    gl.glVertexAttrib1f(loc, 1.0)
    loc = gl.glGetAttribLocation(hprog, 'a_2')
    gl.glVertexAttrib2f(loc, 1.0, 1.0)
    loc = gl.glGetAttribLocation(hprog, 'a_3')
    gl.glVertexAttrib3f(loc, 1.0, 1.0, 1.0)
    loc = gl.glGetAttribLocation(hprog, 'a_4')
    gl.glVertexAttrib4f(loc, 1.0, 1.0, 1.0, 1.0)
    
    # --- flush and finish
    
    # Not really necessary, but we want to touch the functions
    gl.glFlush()
    gl.glFinish()
    
    #print([i[1] for i in objects])
    return objects


def _draw1():
    # Draw using arrays
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, N)
    gl.glFinish()
    _check_result()


def _draw2():
    # Draw using elements via buffer
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, helements)
    gl.glDrawElements(gl.GL_TRIANGLES, elements.size, gl.GL_UNSIGNED_BYTE, 0)
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)
    gl.glFinish()
    _check_result()


def _draw3():
    # Draw using elements via numpy array
    gl.glDrawElements(gl.GL_TRIANGLES, 
                      elements.size, gl.GL_UNSIGNED_BYTE, elements)
    gl.glFinish()
    _check_result()


def _check_result(assert_result=True):
    """ Test the color of each quadrant by picking the center pixel 
    of each quadrant and comparing it with the reference color.
    """
    
    # Take screenshot
    x, y, w, h = gl.glGetParameter(gl.GL_VIEWPORT)
    data = gl.glReadPixels(x, y, w, h, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
    im = np.frombuffer(data, np.uint8)
    im.shape = h, w, 3
    
    # Get center pixel from each quadrant
    pix1 = tuple(im[int(1*h/4), int(1*w/4)])
    pix2 = tuple(im[int(3*h/4), int(1*w/4)])
    pix3 = tuple(im[int(3*h/4), int(3*w/4)])
    pix4 = tuple(im[int(1*h/4), int(3*w/4)])
    #print(pix1, pix2, pix3, pix4)
   
    if assert_result:
        # Test their value
        assert_equal(pix1, (0, 0, 0))
        assert_equal(pix2, (255, 0, 0))
        assert_equal(pix3, (0, 255, 0))
        assert_equal(pix4, (0, 0, 255))


run_tests_if_main()
