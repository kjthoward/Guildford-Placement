import pydicom

import skimage
import skimage.feature
import skimage.viewer
import sys
import pdb

ds = pydicom.dcmread("./Implants/1.2.826.0.1.3680043.9.3218.1.1.42920551.6463.1537595412629.418.0.dcm")
image=ds.pixel_array
rows, cols = image.shape
#pdb.set_trace()
pixels_intensity=round(image.max()*0.75)
mask = image < pixels_intensity
image[mask]=0
if "R" not in ds.SeriesDescription:
    image=image[:,:int(cols/2)]
viewer = skimage.viewer.ImageViewer(image)

canny_plugin = skimage.viewer.plugins.Plugin(image_filter=skimage.feature.canny)
canny_plugin.name = "Canny Filter Plugin"

canny_plugin += skimage.viewer.widgets.Slider(
    name="sigma", low=0.0, high=15.0, value=15.0
)
canny_plugin += skimage.viewer.widgets.Slider(
    name="low_threshold", low=0.0, high=50.0, value=0
)
canny_plugin += skimage.viewer.widgets.Slider(
    name="high_threshold", low=0.0, high=1000.0, value=10
)

viewer += canny_plugin
viewer.show()
