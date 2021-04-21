from detection.Form import *
import os
import cv2

bad_inputs = []
dir = 'E:/Mulong/Datasets/form/input'
for file in os.listdir(dir):
    img_path = dir + '/' + file
    print(img_path)
    try:
        form_compo_detection(img_path, resize_height=None, export_dir='E:/Mulong/Datasets/form/output')
        print()
    except e as e:
        bad_inputs.append(img_path)
        print(e)
        continue
print(bad_inputs)
