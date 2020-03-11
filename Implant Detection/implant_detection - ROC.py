import pydicom
import os
import matplotlib.pyplot as plt
import numpy as np
import pickle
from skimage import filters, feature
import skimage.segmentation as seg
import scipy.ndimage as ndi
from skimage.util import img_as_float
import pdb
from skimage.measure import ransac, CircleModel
import matplotlib.pyplot as plt
import sys


#True will show implants as they are found
show=False

#number of attempts per image (to average out RANSAC errors)
#Will change to args later
attempts=5

#will change folderpath to args etc... later
folderpath="/Users/kieranhoward/Documents/Organised/Silicone Implant"

#Change to change the name of the pickle file it checks/loads/saves
file="NEW_implant_results_POS2_fine_windowed.pickle"

folderpath="./Implants"

"""RESULTS:


"""

#shows the combinations that had the highest detection
def get_best(array):
    best=0
    combo=[]
    for pixel, values in array.items():
        for area, item in values.items():
            if item["detected"]>best:
                combo=[(pixel,area)]
                best=item["detected"]
            elif item["detected"]==best:
                combo.append((pixel,area))
    return best, combo

#Gets lowest values, used for negatives
def get_worst(array):
    worst=100000000000000
    combo=[]
    for pixel, values in array.items():
        for area, item in values.items():
            if item["detected"]<worst:
                combo=[(pixel,area)]
                best=item["detected"]
            elif item["detected"]==worst:
                combo.append((pixel,area))
    return worst, combo

detected_implant_count=0
dicom_implant_count=0
file_count=0


def DetectImplant(array, pixel, area):
    image=array.copy()
    original=image.copy()
    """Takes a Grey-Scale image (e.g dicom pixel array) and calculates the percentage
    of pixels that are above an intensity threshold within the most circular object in the image.

    Returns True if more than x percentage of the image is greater than y percentage of maximum intensity"""

    
    #percentile for pixels to be in to be considered "implant bright"
    pixel_threshold=pixel

    #percentage of the image that needs to be "implant bright" to trigger implant detection
    area_threshold=area
    
    global detected_implant_count, dicom_implant_count

    rows, cols = image.shape
    #Cuts image in half (taking left or right depending on image
    try:
        if re.match(r"L.*MLO",ds.SeriesDescription) or re.match(r"L.*CC", ds.SeriesDescription):
            image=image[:,:int(cols/2)]    
        elif re.match(r"R.*MLO",ds.SeriesDescription) or re.match(r"R.*CC", ds.SeriesDescription):
            image=image[:,int(cols/2):]
        elif "L" in ds.PatientOrientation[1]:
            image=image[:,:int(cols/2)]
        elif "R" in ds.PatientOrientation[1]:
            image=image[:,int(cols/2):]
    except:
        pass
    
    
    cropped=image.copy()
    #resets dimensions for the new, cropped, image
    rows, cols = image.shape
    #Calculates true area of the image, based on pixels that are not zero
    AOI=np.count_nonzero(image)
    #resets image if AOI is too low (e.g DiCom tag mis entered for Left/Right
    if AOI<75000:
        image=original.copy()
        cropped=original.copy()
        rows, cols = image.shape
        AOI=np.count_nonzero(image)
    #calculates minimum pixel intensity required for a pixel to be "implant bright"
    pixels_intensity=round(image.max()*pixel_threshold)

    try:
        #'pre-mask' to filter out tisue/breast outline etc... (as breast outline is
        #also circular it causes inconsitency in the RANSAC
        mask = image<round(image.max()*0.80)
        image[mask]=0
        #creates a circular mask around the most circular object, helps to limit intensity search to implant only
        #and also for magviews the circle is the middle of the magview, so all the white metal
        #around the circle gets blacked out (jsut doing intensity some magviews were implant positive)
        edges = feature.canny(image, sigma=10, low_threshold=10, high_threshold=500)
        points = np.array(np.nonzero(edges)).T
        model_robust, inliers = ransac(points, CircleModel, min_samples=5,
                                       residual_threshold=1, max_trials=100)
        cy, cx, r = model_robust.params
        y,x=np.ogrid[-cy:rows-cy, -cx:cols-cx]
        mask = x*x + y*y <= r*r
        #as mask is the circle, ~mask inverts it
        #Sometimes mask is 1-2 pixels larger than image (not sure why)
        #[:rows, :cols] only applies mask where there is image
        image[~mask[:rows,:cols]]=0
    except Exception as e:
        pass
    #zeros out all pixels below the threshold
    mask = image < pixels_intensity
    image[mask]=0


    #gets area of pixels that are above threshold
    IMP_area=np.count_nonzero(image)

    try:
        percent=IMP_area/AOI
    except Exception as e:
        print(e)
        pdb.set_trace()
    if show==True:
        f, (ax0, ax1, ax2, ax3) = plt.subplots(1, 4, figsize=(15, 8))
        ax0.imshow(original, cmap=plt.cm.bone)
        ax0.set_title("ORIGINAL")

        ax1.imshow(cropped>(round(image.max()*0.90)), cmap=plt.cm.bone)
        ax1.set_title("FIRST THRESH")
        
        ax2.imshow(cropped, cmap=plt.cm.bone)
        circle = plt.Circle((cx, cy), radius=r, facecolor='r', linewidth=2)
        ax2.add_patch(circle)
        ax2.set_title("CIRCLE MASK")

        ax3.imshow(image, cmap=plt.cm.bone)
        ax3.set_title("PIXELS COUTNING FOR 'IMPLANT'")

        plt.show()
    if percent>area_threshold:
        return True
                
                
results={}
pixel=0.80
if not os.path.exists(file):
    while pixel<1.0001:
        #round as 0.1+0.1+0.1 = 0.30000000000004....
        pixel=round(pixel,3)
        results[pixel]={}
        area=0.1
        while area<0.5000001:
            area=round(area,3)
            results[pixel][area]={}
            print(f"Pixel: {pixel}, Area {area}")
            detected_implant_count=0
            filecount=0
            for root, dirs, files in os.walk(folderpath):
                for file in files:
                    if file.endswith(".dcm"):
                        ds=pydicom.dcmread(os.path.join(root,file))
                        filecount+=1                        
                        called=0
                        for i in range(attempts):
                            if DetectImplant(ds.pixel_array, pixel=pixel, area=area)==True:
                                called+=1
                        if called>(attempts*0.75):
                            detected_implant_count+=1
            #good for human readable... need to change for actually storing/processing results
            results[pixel][area]["detected"]=detected_implant_count
            results[pixel][area]["expected"]=filecount
            area+=0.01
        pixel+=0.01
    pickle.dump(results,open(file,"wb"))
else:
    results=pickle.load(open(file,"rb"))

#sys.exit()

highest, high_combos = get_best(results)
lowest, low_combos = get_worst(results)
print("CONTINUE?")
pdb.set_trace()
i=1
num_plots=len(results)+1
fig = plt.figure(figsize=(20,10))
for k, v in results.items():
    ax=fig.add_subplot(int(num_plots/4),4,i)
    pixel=k
    detected=[]
    areas=[]
    for area, values in v.items():
        areas+=[area]
        detected+=[(values["detected"]/values["expected"])*100]
    ax.plot(areas,detected)
    
    ax.set_title(f"\nPixel Threshold: {pixel}")
    ax.set_xlabel("Area Threshold")
    ax.set_ylabel("Percentage Detected")
    
    i+=1
plt.tight_layout()
fig.show()
