# -*- coding: utf-8 -*-
# vispy: testskip
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
An oscilloscope, spectrum analyzer, and spectrogram.

This demo uses pyaudio to record data from the microphone. If pyaudio is not
available, then a signal will be generated instead.
"""

from __future__ import division

import threading
import atexit
import numpy as np
from vispy import app, scene, gloo, visuals
from vispy.util.filter import gaussian_filter

try:
    import pyaudio
    
    class MicrophoneRecorder(object):
        def __init__(self, rate=44100, chunksize=1024):
            self.rate = rate
            self.chunksize = chunksize
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=self.rate,
                                      input=True,
                                      frames_per_buffer=self.chunksize,
                                      stream_callback=self.new_frame)
            self.lock = threading.Lock()
            self.stop = False
            self.frames = []
            atexit.register(self.close)

        def new_frame(self, data, frame_count, time_info, status):
            data = np.fromstring(data, 'int16')
            with self.lock:
                self.frames.append(data)
                if self.stop:
                    return None, pyaudio.paComplete
            return None, pyaudio.paContinue
        
        def get_frames(self):
            with self.lock:
                frames = self.frames
                self.frames = []
                return frames
        
        def start(self):
            self.stream.start_stream()
    
        def close(self):
            with self.lock:
                self.stop = True
            self.stream.close()
            self.p.terminate()

except ImportError:
    class MicrophoneRecorder(object):
        def __init__(self):
            self.chunksize = 1024
            self.rate = rate = 44100.
            t = np.linspace(0, 10, rate*10)
            self.data = (np.sin(t * 10.) * 0.3).astype('float32')
            self.data += np.sin((t + 0.3) * 20.) * 0.15
            self.data += gaussian_filter(np.random.normal(size=self.data.shape)
                                         * 0.2, (0.4, 8))
            self.data += gaussian_filter(np.random.normal(size=self.data.shape)
                                         * 0.005, (0, 1))
            self.data += np.sin(t * 1760 * np.pi)  # 880 Hz
            self.data = (self.data * 2**10 - 2**9).astype('int16')
            self.ptr = 0
            
        def get_frames(self):
            if self.ptr + 1024 > len(self.data):
                end = 1024 - (len(self.data) - self.ptr)
                frame = np.concatenate((self.data[self.ptr:], self.data[:end]))
            else:
                frame = self.data[self.ptr:self.ptr+1024]
            self.ptr = (self.ptr + 1024) % (len(self.data) - 1024)
            return [frame]
        
        def start(self):
            pass


class Oscilloscope(scene.ScrollingLines):
    """A set of lines that are temporally aligned on a trigger.
    
    Data is added in chunks to the oscilloscope, and each new chunk creates a
    new line to draw. Older lines are slowly faded out until they are removed.
    
    Parameters
    ----------
    n_lines : int
        The maximum number of lines to draw.
    line_size : int
        The number of samples in each line.
    dx : float
        The x spacing between adjacent samples in a line.
    color : tuple
        The base color to use when drawing lines. Older lines are faded by
        decreasing their alpha value.
    trigger : tuple
        A set of parameters (level, height, width) that determine how triggers
        are detected.
    parent : Node
        An optional parent scenegraph node.
    """
    def __init__(self, n_lines=100, line_size=1024, dx=1e-4,
                 color=(20, 255, 50), trigger=(0, 0.002, 1e-4), parent=None):
        
        self._trigger = trigger  # trigger_level, trigger_height, trigger_width
        
        # lateral positioning for trigger
        self.pos_offset = np.zeros((n_lines, 3), dtype=np.float32)
        
        # color array to fade out older plots
        self.color = np.empty((n_lines, 4), dtype=np.ubyte)
        self.color[:, :3] = [list(color)]
        self.color[:, 3] = 0
        self._dim_speed = 0.01 ** (1 / n_lines)
        
        self.frames = []  # running list of recently received frames
        self.plot_ptr = 0
        
        scene.ScrollingLines.__init__(self, n_lines=n_lines,
                                      line_size=line_size, dx=dx,
                                      color=self.color,
                                      pos_offset=self.pos_offset,
                                      parent=parent)
        self.set_gl_state('additive', line_width=2)
        
    def new_frame(self, data):
        self.frames.append(data)
        
        # see if we can discard older frames
        while len(self.frames) > 10:
            self.frames.pop(0)
        
        if self._trigger is None:
            dx = 0
        else:
            # search for next trigger
            th = self._trigger[1]  # trigger window height
            tw = self._trigger[2] / self._dx  # trigger window width
            thresh = self._trigger[0]

            trig = np.argwhere((data[tw:] > thresh + th) & 
                               (data[:-tw] < thresh - th))
            if len(trig) > 0:
                m = np.argmin(np.abs(trig - len(data) / 2))
                i = trig[m, 0]
                y1 = data[i]
                y2 = data[min(i + tw * 2, len(data) - 1)]
                s = y2 / (y2 - y1)
                i = i + tw * 2 * (1-s)
                dx = i * self._dx
            else:
                # default trigger at center of trace
                # (optionally we could skip plotting instead, or place this 
                # after the most recent trace)
                dx = self._dx * len(data) / 2.
            
        # if a trigger was found, add new data to the plot
        self.plot(data, -dx)
        
    def plot(self, data, dx=0):
        self.set_data(self.plot_ptr, data)
        
        self.color[..., 3] *= 0.98
        self.color[self.plot_ptr, 3] = 50
        self.set_color(self.color)
        self.pos_offset[self.plot_ptr] = (dx, 0, 0)
        self.set_pos_offset(self.pos_offset)
        
        self.plot_ptr = (self.plot_ptr + 1) % self._data_shape[0]


rolling_tex = """
float rolling_texture(vec2 pos) {
    if( pos.x < 0 || pos.x > 1 || pos.y < 0 || pos.y > 1 ) {
        return 0.0f;
    }
    vec2 uv = vec2(mod(pos.x+$shift, 1), pos.y);
    return texture2D($texture, uv).r;
}
"""

cmap = """
vec4 colormap(float x) {
    x = x - 1e4;
    return vec4(x/5e6, x/2e5, x/1e4, 1); 
}
"""


class ScrollingImage(scene.Image):
    def __init__(self, shape, parent):
        self._shape = shape
        self._color_fn = visuals.shaders.Function(rolling_tex)
        self._ctex = gloo.Texture2D(np.zeros(shape+(1,), dtype='float32'),
                                    format='luminance', internalformat='r32f')
        self._color_fn['texture'] = self._ctex
        self._color_fn['shift'] = 0
        self.ptr = 0
        scene.Image.__init__(self, method='impostor', parent=parent)
        #self.set_gl_state('additive', cull_face=False)
        self.shared_program.frag['get_data'] = self._color_fn
        cfun = visuals.shaders.Function(cmap)
        self.shared_program.frag['color_transform'] = cfun
        
    @property
    def size(self):
        return self._shape

    def roll(self, data):
        data = data.reshape(data.shape[0], 1, 1)
        
        self._ctex[:, self.ptr] = data
        self._color_fn['shift'] = (self.ptr+1) / self._shape[1]
        self.ptr = (self.ptr + 1) % self._shape[1]
        self.update()

    def _prepare_draw(self, view):
        if self._need_vertex_update:
            self._build_vertex_data()
            
        if view._need_method_update:
            self._update_method(view)

       
mic = MicrophoneRecorder()
n_fft_frames = 8
fft_samples = mic.chunksize * n_fft_frames

win = scene.SceneCanvas(keys='interactive', show=True, fullscreen=True)
grid = win.central_widget.add_grid()

view3 = grid.add_view(row=0, col=0, col_span=2, camera='panzoom',
                      border_color='grey')
image = ScrollingImage((1 + fft_samples // 2, 4000), parent=view3.scene)
image.transform = scene.LogTransform((0, 10, 0))
#view3.camera.rect = (0, 0, image.size[1], np.log10(image.size[0]))
view3.camera.rect = (3493.32, 1.85943, 605.554, 1.41858)

view1 = grid.add_view(row=1, col=0, camera='panzoom', border_color='grey')
view1.camera.rect = (-0.01, -0.6, 0.02, 1.2)
gridlines = scene.GridLines(color=(1, 1, 1, 0.5), parent=view1.scene)
scope = Oscilloscope(line_size=mic.chunksize, dx=1.0/mic.rate,
                     parent=view1.scene)

view2 = grid.add_view(row=1, col=1, camera='panzoom', border_color='grey')
view2.camera.rect = (0.5, -0.5e6, np.log10(mic.rate/2), 5e6)
lognode = scene.Node(parent=view2.scene)
lognode.transform = scene.LogTransform((10, 0, 0))
gridlines2 = scene.GridLines(color=(1, 1, 1, 1), parent=lognode)

spectrum = Oscilloscope(line_size=1 + fft_samples // 2, n_lines=10,
                        dx=mic.rate/fft_samples,
                        trigger=None, parent=lognode)


mic.start()

window = np.hanning(fft_samples)

fft_frames = []


def update(ev):
    global fft_frames, scope, spectrum, mic
    data = mic.get_frames()
    for frame in data:
        #import scipy.ndimage as ndi
        #frame -= ndi.gaussian_filter(frame, 50)
        #frame -= frame.mean()
        
        scope.new_frame(frame)
        
        fft_frames.append(frame)
        if len(fft_frames) >= n_fft_frames:
            cframes = np.concatenate(fft_frames) * window
            fft = np.abs(np.fft.rfft(cframes)).astype('float32')
            fft_frames.pop(0)
            
            spectrum.new_frame(fft)
            image.roll(fft)


timer = app.Timer(interval='auto', connect=update)
timer.start()

if __name__ == '__main__':
    app.run()
