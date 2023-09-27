import os
import pydicom

saved_path = "New_Data/New_Dicom_1/"

new_files = os.listdir(saved_path)

for dicom in new_files:
    dicom_obj_path = os.path.join(saved_path,dicom)
    dicom_obj = pydicom.dcmread(dicom_obj_path)

    print(dicom_obj)
    break
    # checking patient ID in the new dicom files 
    if (0x0010,0x0020) in dicom_obj:
        print("Anonymization not correct")
