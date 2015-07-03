from vispy import app, scene, plot
from vispy.util.filter import gaussian_filter
import numpy as np


# Generate M trials of signal
print("Generating data..")
M = 100
N = 10000
pos = np.empty((M, N, 2), dtype=np.float32)
pos[:,:,0] = np.linspace(-10, 10., N).reshape(1,N)
pos[:,:,1] = np.sin(pos[:,:,0] * 10.) * 0.3
pos[:,:,1] += np.sin((pos[:,:,0]+0.3) * 20.) * 0.15
pos[:,:,1] += gaussian_filter(np.random.normal(size=(M,N))*0.2, (0.4, 8))
pos[:,:,1] += gaussian_filter(np.random.normal(size=(M,N))*0.005, (0, 1))

# find trigger locations
print("Triggering..")
trig = []
for i in range(M):
    ind = np.argwhere((pos[i,1:,1]>0) & (pos[i,:-1,1]<0))[:,0]
    ind2 = np.argmin(np.abs(pos[i,1:,0][ind]))
    trig.append(ind[ind2]-(N/2.))

alpha = np.linspace(0, 1, M)


win = scene.SceneCanvas(keys='interactive', show=True)
#plt = plot.PlotWidget(fg_color='w')
#win.central_widget.add_widget(plt)
#view = plt.view
view = win.central_widget.add_view(camera='panzoom')
grid = scene.GridLines(parent=view.scene)


plots = []
for i in range(M):
    plots.append(scene.Line(pos[i], color=(0.1, 1, 0.2, alpha[i]), width=2,
                 parent=view.scene, method='gl', antialias=False))
    plots[-1].set_gl_state('additive')
    plots[-1].transform = scene.STTransform()

view.camera.rect = (-1, -0.6, 2, 1.2)

plot_ptr = 0
data_ptr = 0

def update(ev):
    global plot_ptr, data_ptr, plots, pos
    plots[plot_ptr].set_data(pos[data_ptr])
    dx = -trig[data_ptr] * 20./float(N)
    plots[plot_ptr].transform.translate = (dx, 0)    
    for i in range(len(plots)):
        alpha = 0.5 * ((len(plots)-float(i))/len(plots))**8
        plots[(plot_ptr - i) % len(plots)].set_data(color=(.1, 1.0, .2, alpha))
    data_ptr = (data_ptr + 1) % M
    plot_ptr = (plot_ptr + 1) % len(plots)
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
