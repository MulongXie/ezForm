import cv2
import numpy as np
from random import randint as rint

img = cv2.imread('3.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
canny = cv2.Canny(img, 20, 20)

rec, bin = cv2.threshold(canny, 1, 255, cv2.THRESH_BINARY)

_, contours, _ = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
draw_cnt = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
for i in range(len(contours)):
    cnt = contours[i]
    if cv2.contourArea(cnt) < 100:
        continue
    # cv2.drawContours(draw_cnt, contours, i, (rint(0, 255), rint(0, 255), rint(0, 255)))
    cv2.drawContours(draw_cnt, contours, i, (0, 0, 255))

cv2.imshow('canny', canny)
cv2.imshow('bin', bin)
cv2.imshow('contour', draw_cnt)
cv2.waitKey(0)