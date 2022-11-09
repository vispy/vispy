import dlpack

import ctypes

DLManagedTensor_size = ctypes.c_size_t(ctypes.sizeof(dlpack.DLManagedTensor))

ctypes.pythonapi.PyMem_RawMalloc.restype = ctypes.c_void_p
ctypes.pythonapi.PyMem_RawFree.argtypes = [ctypes.c_void_p]

ctypes.pythonapi.PyCapsule_New.restype = ctypes.py_object
ctypes.pythonapi.PyCapsule_New.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p]

def _manager_ctx(obj) -> ctypes.c_void_p:
    py_obj = ctypes.py_object(obj)
    py_obj_ptr = ctypes.pointer(py_obj)
    ctypes.pythonapi.Py_IncRef(py_obj)
    ctypes.pythonapi.Py_IncRef(ctypes.py_object(py_obj_ptr))
    return ctypes.cast(py_obj_ptr, ctypes.c_void_p)

@ctypes.CFUNCTYPE(None, ctypes.c_void_p)
def _manager_ctx_deleter(handle: ctypes.c_void_p) -> None:
    dl_managed = dlpack.DLManagedTensor.from_address(handle)
    py_obj_ptr = ctypes.cast(
        dl_managed.manager_ctx, ctypes.POINTER(ctypes.py_object)
    )
    py_obj = py_obj_ptr.contents
    ctypes.pythonapi.Py_DecRef(py_obj)
    ctypes.pythonapi.Py_DecRef(ctypes.py_object(py_obj_ptr))
    ctypes.pythonapi.PyMem_RawFree(handle)

@ctypes.CFUNCTYPE(None, ctypes.c_void_p)
def _pycapsule_deleter(handle: ctypes.c_void_p) -> None:
    pycapsule: ctypes.py_object = ctypes.cast(handle, ctypes.py_object)
    if ctypes.pythonapi.PyCapsule_IsValid(pycapsule, dlpack._c_str_dltensor):
        dl_managed = ctypes.pythonapi.PyCapsule_GetPointer(
            pycapsule, dlpack._c_str_dltensor
        )
        _manager_ctx_deleter(dl_managed)
        ctypes.pythonapi.PyCapsule_SetDestructor(pycapsule, None)

def create_dlpack_capsule(obj, ptr, device, dtype, shape, strides = None, byte_offset = 0):
    ndim = len(shape)
    dl_managed = dlpack.DLManagedTensor.from_address(ctypes.pythonapi.PyMem_RawMalloc(DLManagedTensor_size))
    dl_managed.dl_tensor.data = ptr + byte_offset
    dl_managed.dl_tensor.device = device
    dl_managed.dl_tensor.dtype = dtype
    dl_managed.dl_tensor.ndim = ndim
    dl_managed.dl_tensor.shape = (ctypes.c_int64 * ndim)(*shape)
    dl_managed.dl_tensor.strides = (ctypes.c_int64 * ndim)(*strides)
    dl_managed.dl_tensor.byte_offset = 0 # not all backends respect this field yet
    dl_managed.manager_ctx = _manager_ctx(obj)
    dl_managed.deleter = _manager_ctx_deleter
    pycapsule = ctypes.pythonapi.PyCapsule_New(
        ctypes.byref(dl_managed),
        dlpack._c_str_dltensor,
        _pycapsule_deleter,
    )
    return pycapsule
