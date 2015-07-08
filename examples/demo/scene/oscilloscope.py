from __future__ import division
from vispy import app, scene, plot
from vispy.util.filter import gaussian_filter
import numpy as np
import threading

try:
    import pyaudio
    
    class MicrophoneRecorder(object):
        rate = 44100 #Hz
        chunksize = 2048 #samples
        def __init__(self):
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
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()

except ImportError:
    class MicrophoneRecorder(object):
        def __init__(self):
            rate = 44100.
            dt = 1 / rate
            t = np.linspace(0, 10, rate*10)
            self.data = (np.sin(t * 10.) * 0.3).astype('float32')
            self.data += np.sin((t + 0.3) * 20.) * 0.15
            self.data += gaussian_filter(np.random.normal(size=self.data.shape)*0.2, (0.4, 8))
            self.data += gaussian_filter(np.random.normal(size=self.data.shape)*0.005, (0, 1))
            self.ptr = 0
            
        def get_frame(self):
            frame = self.data[self.ptr:self.ptr+1024]
            self.ptr = (self.ptr + 1024) % (len(self.data) - 1024)
            return frame
        
        def start(self):
            pass



class Oscilloscope(scene.ScrollingLines):
    def __init__(self, n_lines=100, line_size=1024, dx=1e-4,
                 color=(20, 255, 50), parent=None):
        
        # lateral positioning for trigger
        self.pos_offset = np.zeros((n_lines, 3), dtype=np.float32)
        
        # color array to fade out older plots
        self.color = np.empty((n_lines, 4), dtype=np.ubyte)
        self.color[:, :3] = [list(color)]
        self.color[:, 3] = 0
        
        self.frames = []  # running list of recently received frames
        self.triggers = []
        self.last_trigger = [0, 0]  # frame_ind, sample_ind
        self.plot_ptr = 0
        
        scene.ScrollingLines.__init__(self, n_lines=n_lines, 
                                      line_size=line_size, dx=dx, color=self.color,
                                    pos_offset=self.pos_offset, parent=parent)
        self.set_gl_state('additive', line_width=2)
        
    def new_frame(self, data):
        self.frames.append(data)
        
        # see if we can discard older frames
        while len(self.frames) > 10:
            self.frames.pop(0)
            self.triggers.pop(0)
            self.last_trigger[0] -= 1
        
        # search for next trigger
        tw = 20  # trigger window width
        th = 0.05  # trigger window height
        
        trig = np.argwhere((data[tw:] > th) & (data[:-tw] < -th))
        self.triggers.append(trig)
        if len(trig) > 0:
            m = np.argmin(np.abs(trig - len(data) / 2))
            i = trig[m, 0]
            y1 = data[i]
            y2 = data[i + tw * 2]
            s = y2 / (y2 - y1)
            i = i + tw * 2 * (1-s)
            dx = i * self._dx
            
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
       

win = scene.SceneCanvas(keys='interactive', show=True)
view = win.central_widget.add_view(camera='panzoom')
view.camera.rect = (-0.02, -0.6, 0.04, 1.2)
grid = scene.GridLines(color=(1, 1, 1, 0.5), parent=view.scene)

mic = MicrophoneRecorder()
plots = Oscilloscope(line_size=mic.chunksize, dx=1.0/mic.rate, parent=view.scene)

mic.start()


def update(ev):
    data = mic.get_frames()
    for frame in data:
        plots.new_frame(frame)


timer = app.Timer(interval='auto', connect=update)
timer.start()

if __name__ == '__main__':
    app.run()
