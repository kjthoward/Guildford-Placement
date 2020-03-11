import pdb
import json
import os

key={"IS": "Silicone Implant",
     "ISaln": "Saline Implant",
     "C": "Metal Clip",
     "E": "Exposure (too bright/too dark)",
     "CL": "Clothing",
     "P": "Medical Port",
     "F": "Finger (or Hand)",
     "FA": "Face",
     "M": "MagView",
     "TB": "Thin Breast Artefact",
     "Col": "Collimator misaligned",
     "O": "Other",
     "NA": "Not acceptable for testing",
     "N": "No Arteface"}

counts={}
filename="dicom_viewer.json"
with open(os.path.join(os.getcwd(),filename),"rt") as jsonf:
    json_obj=json.load(jsonf)

for item in json_obj["figures"]:
    if len(item["paths"])!=1:
        print("more than one path")
        pdb.set_trace()
    file=item["paths"][0]
    comment=item["comment"]
    if comment=="":
        continue
    comments=comment.split("/")
    for comment in comments:
        if comment not in key.keys():
            print("COMMENT NOT IN PLANNED LIST")
            pdb.set_trace()
        else:
            if comment not in counts:
                counts[comment]=0
            counts[comment]+=1
for k, v in counts.items():
    print(f"{key[k]} had {v} occurrences")
print(f"In total {sum([x for x in counts.values()])} comments were applied")
print("END")            

