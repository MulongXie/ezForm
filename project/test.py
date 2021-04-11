from detection.Form import *
import os
import cv2

print(os.listdir('data/input'))
for file in os.listdir('data/input'):
    if file in ('11.JPG'):
        continue
    img_path = 'data/input/' + file
    print(img_path)
    form_compo_detection(img_path, None)

# form_compo_detection('data/input/8.jpg')
