from cuda import cudart

#from . import dlpack, util
import dlpack, util


def cuda_check(ret):
    err = ret[0]
    if err != cudart.cudaError_t.cudaSuccess:
        _, errname = cudart.cudaGetErrorName(err)
        errcode = str(int(err))
        _, errdescr = cudart.cudaGetErrorString(err)
        raise RuntimeError(errdescr.decode() + ' (' + errname.decode() + ' ' + errcode + ')')
    return ret[1:] if len(ret) != 2 else ret[1]

class CudaBuffer:
    class _Mapping:
        def __init__(self, buffer, stream):
            self.buffer = buffer
            self.stream = stream
            self.resource = cuda_check(cudart.cudaGraphicsGLRegisterBuffer(buffer._glir_object.handle, buffer.flags))
            cuda_check(cudart.cudaGraphicsMapResources(1, self.resource, self.stream))
            self.ptr, self.size = cuda_check(cudart.cudaGraphicsResourceGetMappedPointer(self.resource))
        def capsule(self):
            buffer = self.buffer
            return util.create_dlpack_capsule(self, self.ptr, buffer._device, buffer._dtype, buffer._shape, buffer._strides, buffer._byte_offset)
        def __del__(self):
            cuda_check(cudart.cudaGraphicsUnmapResources(1, self.resource, self.stream))
            cuda_check(cudart.cudaGraphicsUnregisterResource(self.resource))
            
    def __init__(self, glir_object, shape, dtype, strides = None, byte_offset = 0, read = False, write = True):
        self._device_type = dlpack.DLDeviceType.kDLCUDA
        self._device_id = 0 # WARNING: hardcoded to device id 0
        self._device = dlpack.DLDevice(self._device_type, self._device_id)
        self._glir_object = glir_object
        self._shape = shape
        self._dtype = dlpack.DLDataType.TYPE_MAP[str(dtype)]
        self._strides = strides
        self._byte_offset = byte_offset
        assert read or write
        if not read:
            self.flags = cudart.cudaGraphicsRegisterFlags.cudaGraphicsRegisterFlagsReadOnly
        elif not write:
            self.flags = cudart.cudaGraphicsRegisterFlags.cudaGraphicsRegisterFlagsWriteDiscard
        else:
            self.flags = cudart.cudaGraphicsRegisterFlags.cudaGraphicsRegisterFlagsNone
            
    def __dlpack__(self, stream=None):
        return self._Mapping(self, stream).capsule()

    def __dlpack_device__(self):
        return self._device_type, self._device_id

if __name__ == '__main__':
    import vispy.app
    import numpy as np, vispy.gloo.glir
    
    vertex = """
        uniform float theta;
        attribute vec4 color;
        attribute vec2 position;
        varying vec4 v_color;
        void main()
        {
            float ct = cos(theta);
            float st = sin(theta);
            float x = 0.75* (position.x*ct - position.y*st);
            float y = 0.75* (position.x*st + position.y*ct);
            gl_Position = vec4(x, y, 0.0, 1.0);
            v_color = color;
        } """
    
    fragment = """
        varying vec4 v_color;
        void main()
        {
            gl_FragColor = v_color;
        } """

    class Canvas(vispy.app.Canvas):
        def __init__(self):
            super().__init__(size=(512, 512), title='Rotating quad',
                             keys='interactive')
            # Build program & data
            print('Sending position buffer to vispy:')

            self.program = vispy.gloo.Program(vertex, fragment, count=4)
            self.program['color'] = [(1, 0, 0, 1), (0, 1, 0, 1),
                                     (0, 0, 1, 1), (1, 1, 0, 1)]
            self.program['position'] = [(-1, -1), (-1, +1),
                                        (+1, -1), (+1, +1)]
            self.program['theta'] = 0.0
    
            self.timer = vispy.app.Timer('auto', self.on_timer)
            self.clock = 0
            self.timer.start()

            vispy.gloo.set_viewport(0, 0, *self.physical_size)
            vispy.gloo.set_clear_color('white')
    
            np_program_buf = self.program._buffer
            np_position_buf = np_program_buf['position']
            print('position buffer =', np_position_buf)

            #self.context.glir.associate(self.program.glir)
            #self.context.glir.flush(self.context.shared.parser)
            self.show()

            byte_offset = np_position_buf.__array_interface__['data'][0] - np_program_buf.__array_interface__['data'][0]
            strides = [stride // np_position_buf.dtype.itemsize for stride in np_position_buf.strides]
            gl_handle = self.context.shared.parser.get_object(self.program['position'].base.id)

            print('Pulling position out:')
            dlpack_buf = CudaBuffer(gl_handle, np_position_buf.shape, np_position_buf.dtype, strides, byte_offset, read = True)
            import torch
            print('position torch tensor = ', torch.from_dlpack(dlpack_buf))
            import cupy
            print('position cupy array = ', cupy.from_dlpack(dlpack_buf))
    

        def on_draw(self, event):
            vispy.gloo.clear()
            self.program.draw('triangle_strip')
    
        def on_resize(self, event):
            vispy.gloo.set_viewport(0, 0, *event.physical_size)
    
        def on_timer(self, event):
            self.clock += 0.001 * 1000.0 / 60.
            self.program['theta'] = self.clock
            self.update()
        
    c = Canvas()
    c.show()
    vispy.app.run()
