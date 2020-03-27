# Guildford-Placement

Respotiory for the work I did as part of my STP placement in Scientific Computing at Royal Surrey County Hospital

## Project Outlines

1. Create a script to detect Artefact in mammogram images (Artefact chose was silicone implant)
    * To determine a data set of different artefact types approximately 10,500 images were manually classified against 13 artefact types:
      * Face (or Glasses) - 53
      * Finger (or Hand) - 8
      * MagView -	125
      * Medical Port - 16
      * Metal Clip - 15
      * No Artefact - 8796
      * Not Acceptable for Testing - 313
      * Other - 384
      * Other Type of Implant - 21
      * Saline Implant - 9
      * Silicone Implant - 384
      * Thin Breast Artefact - 84
2. Create a MySQL database to store the data that was collected, as part of the research, about which images have different types of Artefacts.
3. Create some PHP webpages to view the data, in both tabular and chart form.

## File/Folder Descriptions

* Type Comments.txt - Further descriptions about the artefact types, and the shorthand code that was used to assign them.
* dicom_viewer.json - JSON file outputted by the 'simple dicom viewer' tool that was used to view and assign comments. JSON elements are "Image Path":"Comment".
* json_reader.py - Python script file that reads dicom_viewer.json and counts the number of each artefact.
* Organise.py - Python script that reads dicome_viewer.json and organises the files into folders of that artefact type.

#### Database info - folder of scripts used to populate database

* Count_by_artefact_name.sql - SQL script file to count the number of an artefact type that is in the MySQL database.
* Drop_all.sql - SQL script to remove all tables from the database, was used for testing/changing database schema.
* combined_data.pickle - Pickled dictionary of information to import into the database. As the information was in different places (DICOM files and dicom_viewer.json) it was easier, and faster, to collate the data once and read the pickle file to insert it, rather than have to read all the files everytime.
* data_generator.py - Python file that creates combined_data.pickle
* db_tables.py - Python file of the database schema which is need by SQLalchemy to read/insert into the database.
* odbc.yml - Conda environment configuration file for Python database work.
* populate_db.py - Python file that imports db_tables.py and then reads combined_data.pickle and inserts the data into the database if it isn't already there. If data is already there it gets counted as a duplicate. Number of newly inserted data and duplicated are reported at the end.

#### Implant Detection - folder of scripts used for the Implant Detection

* RANSAC Checker.py - Python file that loads a DICOM file and displays the circular mask applied by the RANSAC algorithm to check it applies the mask to the right area.
* canny limits.py - Python file that loads a DICOM file and creates an interactive tool to change the parameters to show how Canny edge detection performs with different parameters.
* imaging.yml - Conda environment configuration file for Python DICOM reading.
* implant_detection - ROC.py - Python file that detects implants in a folder of DICOM images with different threshold values for evaluating what threshold combination performs best.
* implant_detection.py - Python file that performs Silicone implant detection on a folder of DICOM images. For each image it reports if an implant was detected and then at the end it reports the total number of files checked, the number of implants that were in the DICOM headers and the number of implant the script detected.

#### Webite - folder of PHP scripts for generating webpages to present the data

_NOTE: the $hostname variable will need to be changed to connect to the database as it's currently set to "localhost" for working from home_

* list_images.php - Takes an artefact type as an argument ("?artefact=" in URL) and displays a table of images with that artefact. 
* total_chart.php - Creates a bar chart (using Google Charts API) that shows the total number of images with each artefact type. Mousing over the bar displays the exact number, for artefact types with very low numbers the bar can't be moused over so for these bars an annotation is used to display the number instead. X axis (Artefact Type) labels are also clickable to take you to the list_images.php page for that artefact type.
* total_table.php - Creats a table that shows the number of images with each artefact type. Artefact types are also hyperlinks to take you to the list_images.php page for that artefact type.
