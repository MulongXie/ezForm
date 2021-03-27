import os
import sys
import cv2
import json

form_img_file = sys.argv[1]
form_name = form_img_file.split('/')[-1][:-4]
img = cv2.imread(form_img_file)

output_dir = 'data/output/' + form_name
input_data = json.load(open(output_dir + '/input_data.json', 'r'))['inputs']
input_loc = json.load(open(output_dir + '/input_loc.json', 'r'))
result_img = output_dir + '/filled.jpg'

for ipt in input_data:
    if ipt in input_loc:
        # print(input_data[ipt], input_loc[ipt])
        cv2.putText(img, input_data[ipt], (input_loc[ipt][0]['left']+5, input_loc[ipt][0]['top']+10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0,0,255), 1)
cv2.imwrite(result_img, img)
cv2.imshow('filled', img)
cv2.waitKey()
cv2.destroyWindow('filled')
