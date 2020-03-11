import pdb
import json
import os
import shutil
import datetime

key={"IS": "Silicone Implant",
     "ISal": "Saline Implant",
     "C": "Metal Clip",
     "CL": "Clothing",
     "P": "Medical Port",
     "F": "Finger (or Hand)",
     "FA": "Face (or Glasses)",
     "M": "MagView",
     "TB": "Thin Breast Artefact",
     "Imp": "Other type of Implant",
     "Col": "Collimator misaligned",
     "O": "Other",
     "NA": "Not acceptable for testing",
     "N": "No Artefact"}
start=datetime.datetime.now()

filename="dicom_viewer.json"
DOCS="/Users/kieranhoward/Documents/Organised/"
IMAGES="/Users/kieranhoward/Documents/OMI-DB/image_db/sharing/omi-db/images/"
def create(path):
    if not os.path.exists(path):
        os.mkdir(path)

for value in key.values():
    create(os.path.join(DOCS,value))
with open(os.path.join(os.getcwd(),filename),"rt") as jsonf:
    json_obj=json.load(jsonf)

for item in json_obj["figures"]:
    path=""
    pateint=""
    folder=""
    file=""
    comment=""
    if len(item["paths"])!=1:
        print("more than one path")
        pdb.set_trace()
    path=item["paths"][0]
    patient=path.split('/')[0]
    folder=path.split('/')[1]
    file=path.split('/')[2]
    comment=item["comment"]
    if comment=="":
        continue
    comments=comment.split("/")
    for comment in comments:
        if comment not in key.keys():
            print("COMMENT NOT IN PLANNED LIST")
            pdb.set_trace()
        else:
            create(os.path.join(DOCS,key[comment],patient))
            create(os.path.join(DOCS,key[comment],patient,folder))
            if not os.path.exists(os.path.join(DOCS,key[comment],patient,folder,file)):
                print(f"Copying {path} to {key[comment]}")
                shutil.copy(os.path.join(IMAGES,path),os.path.join(DOCS,key[comment],patient,folder,file))
end=datetime.datetime.now()
print(f"Start datetime {start}")
print(f"End datetime {end}")
print("END")            

