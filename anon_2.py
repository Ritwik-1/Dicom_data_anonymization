import pydicom
import os
import numpy as np
import pandas as pad
import csv
import matplotlib.pyplot as plt
from PIL import Image

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

def window_image(img, window_center,window_width,intercept,slope ,rescale=True):
    img = (img*slope +intercept) #for translation adjustments given in the dicom file.

    window_center = 50
    window_width = 350

    img_min = window_center - window_width//2 #minimum HU level
    img_max = window_center + window_width//2 #maximum HU level
    img[img<img_min] = img_min #set img_min for all HU levels less than minimum HU level
    img[img>img_max] = img_max #set img_max for all HU levels higher than maximum HU level
    if rescale:
        img = (img - img_min) / (img_max - img_min)*255.0
    return img

def get_first_of_dicom_field_as_int(x):
    #get x[0] as in int is x is a 'pydicom.multival.MultiValue', otherwise get int(x)
    if type(x) == pydicom.multival.MultiValue: return int(x[0])
    else: return int(x)

def get_windowing(data):
    dicom_fields = [data[('0028','1050')].value, #window center
                    data[('0028','1051')].value, #window width
                    data[('0028','1052')].value, #intercept
                    data[('0028','1053')].value] #slope
    return [get_first_of_dicom_field_as_int(x) for x in dicom_fields]

# data folder has say x patients and each is a folder with say y dicoms
data_folder_path = "Data/"
save_folder_path = "New_Data/"
png_folder = "Images_png/"

naming_convention = "New_Dicom_"

folders = os.listdir()
print(folders)
if "New_Data" not in folders:
    os.makedirs("New_Data")

if "Images_png" not in folders:
    os.makedirs("Images_png")
 
# mapping for patient ID : (0x0010,0x0020)
patient_ID_mapping = {}
patient_counter = 1

patients = os.listdir(data_folder_path)
for patient in patients:
    dicoms = os.listdir(os.path.join(data_folder_path,patient))
    # make directory for patient in Images_png and New_Data 
    # according to naming convention

    folder_png = os.listdir(png_folder)
    folder_new_data = os.listdir(save_folder_path)

    # *********This naming convention the user can provide
    # common for both png and new data
    folder_name = naming_convention + str(patient_counter)

    # To make patient directory in new directories
    patient_folder_name_png_path = png_folder + "/" + folder_name 
    patient_folder_name_new_data_path = save_folder_path + "/" + folder_name 

    if folder_name not in folder_png:
        os.makedirs(patient_folder_name_png_path)
    if folder_name not in folder_new_data:
        os.makedirs(patient_folder_name_new_data_path)

    slice = 1
    print("Dicoms length : ",len(dicoms))

    for dicom in dicoms:
        dicom_obj_path = os.path.join(os.path.join(data_folder_path,patient),dicom)
        dicom_obj = pydicom.dcmread(dicom_obj_path)

        # mapping patient ID to dictionary
        # ensuring uniqueness of the patient 
        patient_ID_mapping[dicom_obj.PatientID] = patient_counter

        new_dicom = anonimize_file(dicom_obj)

        # output_path = os.path.join(patient_folder_name_new_data_path,f"/slice_{slice}.dcm")
        output_path = patient_folder_name_new_data_path + f"/slice_{slice}.dcm"
        # print("Helle ",output_path)
        new_dicom.save_as(output_path)

        # saving png images for the patient 
        array = new_dicom.pixel_array
        
        window_center , window_width, intercept, slope = get_windowing(dicom_obj)
        array = window_image(array, window_center, window_width, intercept, slope, rescale = True)

        # plt.imshow(array,cmap='gray')
        # plt.show()
        # image = Image.fromarray(array, 'L')
        # image.save(patient_folder_name_png_path+f'/slice_{slice}.png')
        plt.imsave(patient_folder_name_png_path+f'/slice_{slice}.png',array, cmap='gray')
        
        slice+=1
    patient_counter += 1

    # saving a CSV file for mapping
    output_file_path = save_folder_path + 'mapping.csv'

    with open(output_file_path, 'w', newline='') as csvfile:
        fieldnames = ['PatientID', 'mapping']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for key, value in patient_ID_mapping.items():
            writer.writerow({'PatientID': key, 'mapping': value})




