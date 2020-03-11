import pdb
import json
import os
import pickle
import pydicom
import sys

key={"IS": "Silicone Implant",
     "ISal": "Saline Implant",
     "C": "Metal Clip",
     "CL": "Clothing",
     "P": "Medical Port",
     "F": "Finger (or Hand)",
     "FA": "Face (or Glasses)",
     "M": "MagView",
     "TB": "Thin Breast Artefact",
     "Col": "Collimator Misaligned",
     "O": "Other",
     "Imp": "Other Type of Implant",
     "NA": "Not Acceptable for Testing",
     "N": "No Artefact"}

#Duplicates as in some images the laterality is in position too
position_key={"MLO": "Mediolateral Oblique",
              "RMLO": "Mediolateral Oblique",
              "LMLO": "Mediolateral Oblique",
              "ML": "Mediolateral",
              "LM": "Lateromedial",
              "CC": "Cranial-Caudal",
              "RCC": "Cranial-Caudal",
              "LCC": "Cranial-Caudal",
              "XCCL": "Exaggerated-Cranio-Caudal"}

laterality_key={"L":"Left",
               "R":"Right",
               "ML":"Left",
               "MR":"Right"}

pickle_file="combined_data1.pickle"
count=1
if not os.path.exists(pickle_file):

    data={}
    filename="../dicom_viewer.json"
    #base path to images, json only stores path relative to this folder
    base='/Users/kieranhoward/Documents/OMI-DB/image_db/sharing/omi-db/images'
    with open(os.path.join(os.getcwd(),filename),"rt") as jsonf:
        json_obj=json.load(jsonf)

    for item in json_obj["figures"]:
        count+=1
        #error catching incase there's more than one path per file (should never happen)
        #so pdb pauses so can investigate
        if len(item["paths"])!=1:
            print("more than one path")
            pdb.set_trace()
        file=item["paths"][0]
        patient,study,image=file.split('/')
        
        comment=item["comment"]

        #skips those without comments applied
        if comment=="":
            continue
        comments=comment.split("/")

        ds=pydicom.dcmread(os.path.join(base,file))
        try:
            position=position_key[ds.ViewPosition]
        except Exception as e:
            if type(e)!=AttributeError:
                print(f"{e} - POSITION")
                print(file)
            position="NOT AVAILIBLE"
        try:
            laterality=laterality_key[ds.ImageLaterality]
        except Exception as e:
            if type(e)!=AttributeError:
                print(f"{e} - LATERALITY")
                print(file)
            if laterality=='':
                laterality="NOT AVAILIBLE"
            laterality="NOT AVAILIBLE"
        
        try:
            implant=ds.BreastImplantPresent
        except Exception as e:
            implant="NOT RECORDED"
        try:
            body_part=ds.BodyPartExamined
        except Exception as e:
            body_part="NOT RECORDED"   
        if patient not in data.keys():
            data[patient]={}
        if study not in data[patient].keys():
            data[patient][study]={}
        try:
            data[patient][study][image]={}
            data[patient][study][image]["implant"]=1 if implant.upper()=="YES" else 0
            data[patient][study][image]["body_part"]=body_part
            data[patient][study][image]["position"]=position
            data[patient][study][image]["laterality"]=laterality
            data[patient][study][image]["comments"]=[key[c] for c in comments]
        except Exception as e:
            print(f"{e} - error in storage")
            pdb.set_trace()
        #pdb.set_trace()
                
          
    pickle.dump(data,open(pickle_file,"wb"))
else:
    data=pickle.load(open(pickle_file,"rb"))
#count is number of items checked
print(count)
#len(data) is number of unique patients
print(len(data))
