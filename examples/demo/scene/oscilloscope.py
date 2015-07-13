from __future__ import division
from vispy import app, scene, plot
from vispy.util.filter import gaussian_filter
import numpy as np
import threading

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
                 color=(20, 255, 50), trigger=(0, 0.05, 5e-4), parent=None):
        
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
                                      line_size=line_size, dx=dx, color=self.color,
                                    pos_offset=self.pos_offset, parent=parent)
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
            
            trig = np.argwhere((data[tw:] > thresh+th) & (data[:-tw] < thresh-th))
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
       
mic = MicrophoneRecorder()

win = scene.SceneCanvas(keys='interactive', show=True)
grid = win.central_widget.add_grid()

view1 = grid.add_view(row=0, col=0, camera='panzoom', border_color='grey')
view1.camera.rect = (-0.01, -0.6, 0.02, 1.2)
gridlines = scene.GridLines(color=(1, 1, 1, 0.5), parent=view1.scene)
scope = Oscilloscope(line_size=mic.chunksize, dx=1.0/mic.rate, parent=view1.scene)

view2 = grid.add_view(row=1, col=0, camera='panzoom', border_color='grey')
view2.camera.rect = (0.5, -0.5e6, np.log10(mic.rate/2), 5e6)
lognode = scene.Node(parent=view2.scene)
lognode.transform = scene.LogTransform((10, 0, 0))
gridlines2 = scene.GridLines(color=(1, 1, 1, 1), parent=lognode)

n_fft_frames = 8
fft_samples = mic.chunksize * n_fft_frames
spectrum = Oscilloscope(line_size=fft_samples/2, n_lines=10, dx=mic.rate/fft_samples,
                        trigger=None, parent=lognode)

mic.start()

window = np.hanning(fft_samples)

fft_frames = []
def update(ev):
    global fft_frames, scope, spectrum, mic
    data = mic.get_frames()
    for frame in data:
        scope.new_frame(frame)
        
        fft_frames.append(frame)
        if len(fft_frames) >= n_fft_frames:
            cframes = np.concatenate(fft_frames) * window
            fft = np.fft.rfft(cframes).astype('float32')
            fft_frames.pop(0)
            spectrum.new_frame(np.abs(fft))


timer = app.Timer(interval='auto', connect=update)
timer.start()

if __name__ == '__main__':
    app.run()
