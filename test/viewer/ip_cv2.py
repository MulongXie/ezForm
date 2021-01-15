import cv2
import numpy as np


img=cv2.imread("1.jpg")
GrayImage=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
ret, th = cv2.threshold(GrayImage,0,255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)
th_blur=cv2.GaussianBlur(th,(5,5),0)
canny_result=cv2.Canny(th_blur,50,200)

_, contours,hierarchy=cv2.findContours(canny_result,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
draw_contour = img.copy()
draw_prox = img.copy()
for cont in contours:
    perimeter = cv2.arcLength(cont,True)
    epsilon = 0.02*cv2.arcLength(cont,True)
    approx = cv2.approxPolyDP(cont,epsilon,True)
    print(len(approx))
    if len(approx) in (2,3,4,5,6) and abs(cv2.contourArea(cont))>100:
        cv2.drawContours(draw_contour, cont, -1, (255,0,0))
        cv2.drawContours(draw_prox, [approx], 0, (0,0,255))

cv2.imshow("contour", draw_contour)
cv2.imshow("prox",draw_prox)
cv2.waitKey(0)
cv2.destroyAllWindows()