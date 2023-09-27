import pydicom
import os
import numpy as np
import pandas as pad
import csv
import matplotlib.pyplot as plt

# tags to be removed
tags = [(0x0009, 0x0010),(0x0010,0x0010),(0x0010,0x0020),(0x0010,0x0030),
        (0x0010,0x0040),(0x0008,0x0080),(0x0008,0x0081),(0x0008,0x0090),
        (0x0008, 0x3010),(0x0010, 0x1010),(0x0008,0x103e),(0x0008,0x1048),
        (0x0008, 0x1050),(0x0008,0x0016),(0x0008,0x0018),(0x0008,0x1110),
        (0x0008, 0x1032),(0x0018,0x9346),(0x0029,0x1140),(0x0032,0x1032),
        (0x0032, 0x1060),(0x0040, 0x0275),(0x0032,0x1064),(0x0002,0x0012),
        (0x0002,0x0013),(0x0008,0x1030),(0x0018,0x1030),(0x0020,0x0052)]

def anonimize_file(dcm_obj):
    for tag in tags:
      if tag in dcm_obj:
          del dcm_obj[tag]
    # else:
    #     print("The specified tag does not exist.")
    return dcm_obj


dicom_folder_path = "Data/"
save_folder_path = "New_Data/"
naming_convention = "New_Dicom_"
png_folder = "Images_png/"


folders = os.listdir()
print(folders)
if "New_Data" not in folders:
    os.makedirs("New_Data")

if "Images_png" not in folders:
    os.makedirs("Images_png")
 
# mapping for patient ID : (0x0010,0x0020)
patient_ID_mapping = {}
patient_counter = 1

dicoms = os.listdir(dicom_folder_path)

for dicom in dicoms:
    dicom_obj_path = os.path.join(dicom_folder_path,dicom)
    dicom_obj = pydicom.dcmread(dicom_obj_path)

    # mapping patient ID to dictionary
    # ensuring uniqueness of the patient 
    if(dicom_obj.PatientID in patient_ID_mapping):
        continue
    patient_ID_mapping[dicom_obj.PatientID] = patient_counter

    new_dicom = anonimize_file(dicom_obj)

    filename = naming_convention + str(patient_counter)
    output_path = os.path.join(save_folder_path,filename)
    new_dicom.save_as(output_path)

    # saving png images for the patient
    patient_folder_name = png_folder + filename 
    array = new_dicom.pixel_array
    
    folder_png = os.listdir(png_folder)

    if patient_folder_name not in folder_png:
        os.makedirs(patient_folder_name)

    print("Hello : ",array.shape)

    break
    for i in range(array.shape[0]):
        slice_image = array[i]
        plt.imsave(patient_folder_name+f'/slice_{i}.png', array, cmap='gray', vmin=0, vmax=1)

    patient_counter += 1

# saving a CSV file for mapping
output_file_path = save_folder_path + 'mapping.csv'

with open(output_file_path, 'w', newline='') as csvfile:
    fieldnames = ['Key', 'Value']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

    for key, value in patient_ID_mapping.items():
        writer.writerow({'Key': key, 'Value': value})




