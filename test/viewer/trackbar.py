import cv2
import numpy as np
from random import randint as rint


def nothing(x):
    pass


img = cv2.imread('3.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

cv2.namedWindow('bar')
cv2.createTrackbar('can-h','bar',0,1000,nothing)
cv2.createTrackbar('can-l','bar',0,2000,nothing)
while True:
    can_h = cv2.getTrackbarPos('can-h', 'bar')
    can_l = cv2.getTrackbarPos('can-l', 'bar')

    canny = cv2.Canny(img, can_h, can_l)
    cv2.imshow('canny', canny)
    cv2.waitKey(10)

    _, contours, _ = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    draw_cnt = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
    # draw_appx = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
    # draw_hull = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
    for i in range(len(contours)):
        cnt = contours[i]
        if cv2.arcLength(cnt, True) < 20:
            continue
        epsilon = 0.005 * cv2.arcLength(cnt, True)
        # approx = cv2.approxPolyDP(cnt, epsilon, True)
        # hull = cv2.convexHull(approx)

        cv2.drawContours(draw_cnt, contours, i, (rint(0,255), rint(0,255), rint(0,255)))
        # cv2.drawContours(draw_appx, [approx], 0, (rint(0,255), rint(0,255), rint(0,255)))
        # cv2.drawContours(draw_hull, [hull], 0, (rint(0,255), rint(0,255), rint(0,255)))

    cv2.imshow('contour', draw_cnt)
    # cv2.imshow('approximate', draw_appx)
    # cv2.imshow('hull', draw_hull)
    cv2.waitKey(10)
