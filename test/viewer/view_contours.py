import cv2
import numpy as np


img = cv2.imread("1.jpg")
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
ret, th = cv2.threshold(gray,0,255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)
th_blur=cv2.GaussianBlur(th,(5,5),0)
canny_result=cv2.Canny(th_blur,50,200)

_, contours,hierarchy=cv2.findContours(canny_result,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
for i, cnt in enumerate(contours):
    if abs(cv2.contourArea(cnt))>100:
        draw_contour_bin = np.zeros((img.shape[0], img.shape[1]))
        draw_contour = img.copy()
        cv2.drawContours(draw_contour_bin, cnt, -1, (255,0,0))
        cv2.drawContours(draw_contour, cnt, -1, (255,0,0))
        cv2.imshow("contour_bin", draw_contour_bin)
        cv2.imshow("contour", draw_contour)
        cv2.waitKey(0)