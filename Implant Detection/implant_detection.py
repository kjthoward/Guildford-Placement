import pydicom
import os
import matplotlib.pyplot as plt
import numpy as np
from skimage import filters, feature
import skimage.segmentation as seg
import scipy.ndimage as ndi
from skimage.util import img_as_float
import pdb
from skimage.measure import ransac, CircleModel
import re

#True will show image, and masks for every item
show=False

#number of attempts per image (to average out RANSAC errors)
#Will change to args later
attempts=5

#will change folderpath to args etc... later
#folderpath="/Users/kieranhoward/Documents/Organised/Thin Breast Artefact"

folderpath="./Implants"

"""RESULTS:
(All implants found in non implant folders were manually checked to be correct)
<FOLDER> : <DETECTED>/<EXPECTED> (<TOTAL FILES IN FOLDER>)
Collimator misaligned: 0/0 (334 checked)
Face (or Glasses): 1/1 (53 checked)
Finger (or Hand): 0/0 (8 checked)
MagView: 0/0 (134 checked)
Medical Port: 0/1 (16 checked) - There is one in DiCom Header, however cannot be seen in the image ?wrong tag
Metal Clip: 0/0 (15 checked)
No Artefact: 0/0 (8,796 checked)
Not acceptable for testing: 8/0 (303 checked) - likely due to large, bright, things like biopsy equipment etc...
Other: 0/0 (384 checked)
Other type of implant: 0/1 (21 checked) - There is one in DiCom Header, however cannot be seen in the image ?wrong tag
Saline Implant: 0/0 (9 checked) - not detected as more faint
Silicone Implant: 54/51 (55 checked) - missed are very small on scan, extra are from wrong tags
Thin Breast Artefact: 0/0 (84 checked)

"""

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
    #Cuts image in half (taking left or right depending on image)
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

    #Sets lowest pixel value to 0, incase there is background 'light' making
    #the background of the image not 0
    bg_mask=image<image.min()
    image[bg_mask]=0
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
        return False
    #zeros out all pixels below the threshold
    mask = image < pixels_intensity
    image[mask]=0


    #gets area of pixels that are above threshold
    IMP_area=np.count_nonzero(image)

    percent=IMP_area/AOI
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
                
    
for root, dirs, files in os.walk(folderpath):
    for file in files:
        if file.endswith(".dcm"):
            ds=pydicom.dcmread(os.path.join(root,file),force=True)
            #skips MONOCHROME 1 files (ones that appear as an all white breast)
            if ds.PhotometricInterpretation=="MONOCHROME1":
                continue
            #skips ones that aren't "for presentation":
            if ds.PresentationIntentType!="FOR PRESENTATION":
                continue
            file_count+=1
            print(f"checking: {file}")
            called=0
            try:
                if ds.BodyPartExamined.upper()!="BREAST":
                    print(f"{file} is not of type 'BREAST'")

            except:
                pass
            for i in range(attempts):
                
                if DetectImplant(ds.pixel_array, pixel=0.90, area=0.18)==True:  
                    called+=1
            try:
                if ds.BreastImplantPresent=="YES":
                    dicom_implant_count+=1
            except Exception as e:
                #print(e)
                pass
            if called>(attempts*0.75):
                print("CALLED")
                #pdb.set_trace()
                detected_implant_count+=1
            else:
                print("NO")
                
print(f"TOTAL FILES in {os.path.split(folderpath)[1]}: {file_count}")
print(f"IMPLANTS IN DICOM TAGS: {dicom_implant_count}")
print(f"IMPLANTS DETECTED: {detected_implant_count}")


#add odbc link to insert ? with option?
