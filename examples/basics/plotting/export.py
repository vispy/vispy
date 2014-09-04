import vispy.plot as vp

# Create a canvas showing plot data
plt = vp.plot([1,6,2,4,3,8,5,7,6,3])

# Render the canvas scene to a numpy array image
image = plt.export()

# Display the data in the array
vp.image(image)


import sys
if sys.flags.interactive == 0:
    plt.app.run()