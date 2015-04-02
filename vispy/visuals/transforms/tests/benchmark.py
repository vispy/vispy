""" A benchmark for testing performance of different transformations.
"""

import time
import numpy as np
from vispy.visuals.transforms import (NullTransform, DefaultTransform, 
                                      STTransform, AffineTransform)

N = 3000


def test_identity():
    
    trans1 = NullTransform()
    trans2 = NullTransform()
    
    # Mapping
    p = (1, 1, 1)
    t0 = time.time()
    for i in range(N):
        trans1.map(p)
    t1 = time.time() - t0
    
    # Composition
    t0 = time.time()
    for i in range(N):
        trans1 * trans2
    t2 = time.time() - t0
    
    return t1, t2


def test_identity_def():
    
    trans1 = DefaultTransform()
    trans2 = DefaultTransform()
    
    # Mapping
    p = (1, 1, 1)
    t0 = time.time()
    for i in range(N):
        trans1.map(p)
    t1 = time.time() - t0
    
    # Composition
    t0 = time.time()
    for i in range(N):
        trans1 * trans2
    t2 = time.time() - t0
    
    return t1, t2


def test_STTRansform():
    
    #trans1 = STTransform((1,1,1))
    #trans2 = STTransform((2,2,2))
    trans1 = STTransform((1,1,1), (1,1,1))
    trans2 = STTransform((2,2,2), (2,2,2))
    
    # Mapping
    p = (1, 1, 1)
    t0 = time.time()
    for i in range(N):
        trans1.map(p)
    t1 = time.time() - t0
    
    # Composition
    t0 = time.time()
    for i in range(N):
        trans1 * trans2
    t2 = time.time() - t0
    
    return t1, t2


def test_STTRansform_def():
    
    #trans1 = DefaultTransform((1,1,1))
    #trans2 = DefaultTransform((2,2,2))
    trans1 = DefaultTransform((1,1,1), None, (1,1,1))
    trans2 = DefaultTransform((2,2,2), None, (2,2,2))
    
    # Mapping
    p = (1, 1, 1)
    t0 = time.time()
    for i in range(N):
        trans1.map(p)
    t1 = time.time() - t0
    
    # Composition
    t0 = time.time()
    for i in range(N):
        trans1 * trans2
    t2 = time.time() - t0
    
    return t1, t2


def test_Affine():
    m = np.eye(4)
    m[1,2] = 1.2
    
    trans1 = AffineTransform(m)
    trans2 = AffineTransform(m)
    
    # Mapping
    p = (1, 1, 1)
    t0 = time.time()
    for i in range(N):
        trans1.map(p)
    t1 = time.time() - t0
    
    # Composition
    t0 = time.time()
    for i in range(N):
        trans1 * trans2
    t2 = time.time() - t0
    
    return t1, t2


def test_Affine_def():
    
    m = np.eye(4)
    m[1,2] = 1.2
    
    trans1 = DefaultTransform(matrix=m)
    trans2 = DefaultTransform(matrix=m)
    
    # Mapping
    p = (1, 1, 1)
    t0 = time.time()
    for i in range(N):
        trans1.map(p)
    t1 = time.time() - t0
    
    # Composition
    t0 = time.time()
    for i in range(N):
        trans1 * trans2
    t2 = time.time() - t0
    
    return t1, t2


just = 14
def print_times(name, func):
    times = func()
    formatter = '%1.1f ms'
    times = [formatter % (t*1000) for t in times]
    times = [t.rjust(just) for t in times]
    print(name.rjust(just) + ': ' + ''.join(times))



print(''.rjust(just) + '  ' + 'mapping'.rjust(just) + 'composition'.rjust(just))
print_times('Identity', test_identity)
print_times('Def-Identity', test_identity_def)
print_times('STT', test_STTRansform)
print_times('Def-STT', test_STTRansform_def)
print_times('Affine', test_Affine)
print_times('Def-Affine', test_Affine_def)
