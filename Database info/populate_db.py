import pyodbc
import pdb
import pickle
import getpass

from db_tables import *

#loads data from the .pickle file I made earlier (more time efficient to collate and sort
#all the data, then store as a pickle, than try to organise it as time of upload
#also means if there is an error in database update I don't have to re-collect all the data
#which saves time

pickle_file="combined_data.pickle"
data=pickle.load(open(pickle_file,"rb"))

#connects to the database, function used so can use recursion if connection fails
#could also be done with while True: then break if connected.
def connect():
    server="10.161.128.46:3306/artifactdb"
    user=input(f"Enter MySQL Username for an account on {server} - ")
    password=getpass.getpass(f"Please enter password for {user} - ")
    engine_temp=create_engine(f'mysql://{user}:{password}@{server}')
    try:
        engine_temp.connect()
        print("LOGIN OK")
        return engine_temp
    except:
        print("DETAILS INCORRECT\nPlease Try Again")
        #return is needed on the negative to solve the recursion error (return returns
        #to whatever called it, so just having connect() here would later return to itself (that called it)
        #and not to the engine=connect() call, returning the recursion means it will
        #"work it's way back up" through the recursion/return layers.
        return connect()

engine=connect()

#uncomment to instead use a local sqlite3 database
##engine=create_engine('sqlite:///' + "artefact.sqlite3")

#creates tables if they don't exist (default is create if not exist, so not other arguments needed)
metadata.create_all(engine)

#function to get foreign key (id) or create the record if it doesn't exist
def get_fk(table,column,value, patient_id=None):
    global conn
    sql=select([table.c.id]) .select_from(table) .where(column==value)
    results=conn.execute(sql).fetchall()
    if len(results)>1:
        print("MORE THAN 1 RESULT??")
        pdb.set_trace()
    elif len(results)==1:
        return results[0][0]
    elif results==[]:
        ins=table.insert().values({column.name:value})
        if patient_id!=None:
            ins=table.insert().values({column.name:value,studies.c.patient_id:patient_id})
        result=conn.execute(ins)
        results = result.inserted_primary_key[0]
        if type(results)==tuple:
            results=results[0]
        return results
    else:
        print("NO RESULT?")
        pdb.set_trace()

inserted=0
dupes=0
with engine.connect() as conn:
    for patient, items in data.items():
        patient_id=get_fk(patients,patients.c.name, patient)
        for study, values in items.items():
            study_id=get_fk(studies,studies.c.study_uid, study, patient_id)
            for image, results in values.items():
                to_ins={}
                to_ins["image_uid"]=image
                to_ins["study_id"]=study_id
                to_ins["position_id"]=get_fk(positions, positions.c.position, results["position"])
                to_ins["laterality_id"]=get_fk(laterality, laterality.c.direction, results["laterality"])
                to_ins["implant_in_header"]=results["implant"]
                to_ins["body_part_imaged_id"]=get_fk(body_part, body_part.c.name, results["body_part"])
                try:
                    insert_statement=images.insert().values(to_ins)
                    conn.execute(insert_statement)
                except Exception as e:
                    if type(e)!=IntegrityError:
                        print(f"Unexpected error of type {type(e)}")
                        pdb.set_trace()
                    else:
                        pass

                #Tries to insert image_artefact information, was previously in same
                #section as image insert but if an image already exists but it's artefact
                #entry does not (e.g adding new artefact type to image that exists it
                #would break on the image unique constraint

                artefact_ins={}
                artefact_ins["image_uid"]=image
                for c in results["comments"]:
                    artefact_ins["artefact_id"]=get_fk(artefact_types, artefact_types.c.name, c)
                    try:
                        art_ins_statement=image_artefacts.insert().values(artefact_ins)
                        conn.execute(art_ins_statement)
                        print(f"inserted {image} - {c}")
                        inserted+=1
                    except Exception as e:
                        if type(e)!=IntegrityError:
                            print(f"Unexpected error of type {type(e)}")
                            pdb.set_trace()
                        else:
                            dupes+=1




print(f"Inserted data for {inserted} images. {dupes} files were already in the database")
