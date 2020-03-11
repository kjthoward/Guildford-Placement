import pydicom
import os
import matplotlib.pyplot as plt
import numpy as np
import pdb
import time
from skimage import filters, feature
import skimage.segmentation as seg
import scipy.ndimage as ndi
from skimage.util import img_as_float
from skimage.feature import peak_local_max
from skimage.draw import circle_perimeter
from skimage.transform import hough_circle, hough_circle_peaks
from skimage import color
from skimage.measure import ransac, CircleModel
ds = pydicom.dcmread("./Implants/1.2.826.0.1.3680043.9.3218.1.1.42920551.6463.1537595412629.392.0.dcm")
image=ds.pixel_array
original=image.copy()
rows, cols = image.shape




if ds.SeriesDescription=="L MLO" or ds.SeriesDescription=="L CC":
    image=image[:,:int(cols/2)]
elif ds.SeriesDescription=="R MLO" or ds.SeriesDescription=="R CC":
    image=image[:,int(cols/2):]
elif "L" in ds.PatientOrientation[1]:
    image=image[:,:int(cols/2)]
elif "R" in ds.PatientOrientation[1]:
    image=image[:,int(cols/2):]
bg_mask=image<image.min()
image[bg_mask]=0
pixels_intensity=round(image.max()*0.8)
mask = image < pixels_intensity
image[mask]=0
edges = feature.canny(image, sigma=15, low_threshold=0, high_threshold=10)
points = np.array(np.nonzero(edges)).T
i=1
while True:
    f, axes = plt.subplots(2,6, figsize=(15, 8))
    axes=axes.ravel()
    axes[0].imshow(original, cmap=plt.cm.bone)
    axes[1].imshow(edges, cmap='gray')

    for ax in axes[2:]:
        
        
        model_robust, inliers = ransac(points, CircleModel, min_samples=5,
                                       residual_threshold=1, max_trials=100)
        cy, cx, r = model_robust.params
         
        
         
        
        ax.imshow(image, cmap=plt.cm.bone)
        #ax2.imshow(image, cmap=plt.cm.bone)
         
         
        circle = plt.Circle((cx, cy), radius=r, facecolor='r', linewidth=2)
        ax.add_patch(circle)
         

    plt.suptitle(f"Run Number {i}")
    i+=1
    plt.show()
#    time.sleep(5)
