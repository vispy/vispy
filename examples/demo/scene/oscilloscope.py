from vispy import app, scene, plot
from vispy.util.filter import gaussian_filter
import numpy as np


# Generate M trials of signal
print("Generating data..")
M = 100
N = 10000
dt = 1e-4
t = np.linspace(0, (N-1)*dt, N).reshape(1, N)
pos = np.empty((M, N), dtype=np.float32)
pos[:] = np.sin(t * 10.) * 0.3
pos[:] += np.sin((t + 0.3) * 20.) * 0.15
pos[:] += gaussian_filter(np.random.normal(size=(M,N))*0.2, (0.4, 8))
#pos[:] += gaussian_filter(np.random.normal(size=(M,N))*0.005, (0, 1))

# find trigger locations
print("Triggering..")
trig = []
for i in range(M):
    # find every location that crosses threshold
    ind = np.argwhere((pos[i,1:]>0) & (pos[i,:-1]<0))[:,0]
    # select the location closest to t=0.5
    ind2 = np.argmin(np.abs(t[0, ind] - 0.5))
    trig.append(ind[ind2])

alpha = np.linspace(0, 1, M)


win = scene.SceneCanvas(keys='interactive', show=True)
view = win.central_widget.add_view(camera='panzoom')
grid = scene.GridLines(parent=view.scene)


pos_offset = np.zeros((M, 3), dtype=np.float32)
plots = scene.ScrollingLines(n_lines=M/2, line_size=N, dx=dt,
                             pos_offset=pos_offset, parent=view.scene)
#plots = []
#for i in range(M):
    #plots.append(scene.Line(pos[i], color=(0.1, 1, 0.2, alpha[i]), width=2,
                 #parent=view.scene, method='gl', antialias=False))
    #plots[-1].set_gl_state('additive')
    #plots[-1].transform = scene.STTransform()

view.camera.rect = (-1, -0.6, 2, 1.2)

plot_ptr = 0
data_ptr = 0



def update(ev):
    global plot_ptr, data_ptr, plots, pos, pos_offset
    plots.set_data(plot_ptr, pos[data_ptr])
    dx = -trig[data_ptr] * dt
    #plots[plot_ptr].transform.translate = (dx, 0)
    #for i in range(len(plots)):
        #alpha = 0.5 * ((len(plots)-float(i))/len(plots))**8
        #plots[(plot_ptr - i) % len(plots)].set_data(color=(.1, 1.0, .2, alpha))
    pos_offset[data_ptr] = (dx, 0, 0)
    plots.set_pos_offset(pos_offset)
    data_ptr = (data_ptr + 1) % M
    plot_ptr = (plot_ptr + 1) % (M/2)
    win.update()
    
@win.connect
def on_key_press(ev):
    if ev.key == 'Space':
        if timer.running:
            timer.stop()
        else:
            timer.start()

timer = app.Timer(interval=0.0, connect=update)
timer.start()

if __name__ == '__main__':
    app.run()
