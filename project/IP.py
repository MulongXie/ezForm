import cv2
import numpy as np


def gray_to_gradient(img):
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_f = np.copy(img)
    img_f = img_f.astype("float")

    kernel_h = np.array([[0,0,0], [0,-1.,1.], [0,0,0]])
    kernel_v = np.array([[0,0,0], [0,-1.,0], [0,1.,0]])
    dst1 = abs(cv2.filter2D(img_f, -1, kernel_h))
    dst2 = abs(cv2.filter2D(img_f, -1, kernel_v))
    gradient = (dst1 + dst2).astype('uint8')
    return gradient


def binarization(org, grad_min, show=False, write_path=None, wait_key=0):
    grey = cv2.cvtColor(org, cv2.COLOR_BGR2GRAY)
    grad = gray_to_gradient(grey)        # get RoI with high gradient
    rec, bin = cv2.threshold(grad, grad_min, 255, cv2.THRESH_BINARY)
    morph = cv2.morphologyEx(bin, cv2.MORPH_CLOSE, (3, 3))  # remove noises
    if write_path is not None:
        cv2.imwrite(write_path, morph)
    if show:
        cv2.imshow('binary', morph)
        if wait_key is not None:
            cv2.waitKey(wait_key)
    return morph


def is_rectangle(contour):
    contour = np.reshape(contour, (-1, 2))
    sides = []
    side = [contour[0], contour[1]]

    # calculate the slope k (y2-y1)/(x2-x1) the first between two neighboor points
    if contour[0][0] == contour[1][0]:
        k_pre = 'v'
    else:
        k_pre = (contour[0][1] - contour[1][1]) / (contour[0][0] - contour[1][0])

    for i, p in enumerate(contour[2:]):
        # calculate the slope k between two neighboor points
        if contour[i][0] == contour[i - 1][0]:
            k = 'v'
        else:
            k = (contour[i][1] - contour[i - 1][1]) / (contour[i][0] - contour[i - 1][0])
        # check if the two points on the same side
        if k != k_pre:
            # leave out noises
            if len(side) >= 4:
                sides.append(side)
            side = [p]
            k_pre = k
        else:
            side.append(p)
    sides.append(side)
    print(len(sides))
    if len(sides) != 4:
        return False
    lens = sorted([len(s) for s in sides])
    if (abs(lens[0] - lens[1]) < 5) and (abs(lens[2] - lens[3]) < 5):
        return True
    return False


img = cv2.imread('1.jpg')
bin = binarization(img, 2, show=False)
draw_contour = img.copy()
_, contours,hierarchy=cv2.findContours(bin,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
for i, cnt in enumerate(contours):
    if abs(cv2.contourArea(cnt)) > 100:
        print(is_rectangle(cnt))
        draw_contour_bin = np.zeros((img.shape[0], img.shape[1]))
        draw_contour = img.copy()
        cv2.drawContours(draw_contour_bin, cnt, -1, (255,0,0))
        cv2.drawContours(draw_contour, cnt, -1, (255,0,0))
        cv2.imshow("contour_bin", draw_contour_bin)
        cv2.imshow("contour", draw_contour)
        cv2.waitKey(0)