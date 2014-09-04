import vispy.plot as vp

# Create a canvas showing plot data
plt = vp.plot([1,6,2,4,3,8,5,7,6,3])

# Render the canvas scene to a numpy array image
image = plt.export()
#plt.app.process_events()
#image = plt.screenshot()

# Display the data in the array
image = image.copy()
plt2 = vp.image(image)

# By default, the view adds some padding when setting its range.
# We'll remove that padding so the image looks exactly like the original 
# canvas:
plt2.view.camera.auto_zoom(plt2.image, padding=0)


import sys
if sys.flags.interactive == 0:
    plt.app.run()