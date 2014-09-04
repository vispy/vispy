import vispy.plot as vp

# Create a canvas showing plot data
plt = vp.plot([1,6,2,4,3,8,5,7,6,3])

# Render the canvas scene to a numpy array image with higher resolution 
# than the original canvas
scale = 4
image = plt.export(size=(plt.size[0]*scale, plt.size[1]*scale))

# Display the data in the array, sub-sampled down to the original canvas
# resolution
image = image[::scale, ::scale]
plt2 = vp.image(image)

# By default, the view adds some padding when setting its range.
# We'll remove that padding so the image looks exactly like the original 
# canvas:
plt2.view.camera.auto_zoom(plt2.image, padding=0)

# Now take a screenshot. This requires having drawn the canvas at least once,
# so we need to call process_events first.
plt.app.process_events()
image = plt.screenshot()



import sys
if sys.flags.interactive == 0:
    plt.app.run()