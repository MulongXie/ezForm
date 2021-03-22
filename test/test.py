import cv2
import numpy as np

img = cv2.imread('1.png')
h,w = img.shape[:2]
mask = np.zeros((h+2,w+2,1),np.uint8)
cv2.floodFill(img,mask,(0,0),(0,0,0),(30,30,30),(30,30,30),cv2.FLOODFILL_FIXED_RANGE)
cv2.imshow('test',img)
cv2.imshow('mask', mask)
cv2.waitKey(0)