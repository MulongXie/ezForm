import cv2
import numpy as np


class Image:
    def __init__(self, img_file_name):
        self.img_file_name = img_file_name
        self.img = cv2.imread(img_file_name)
        self.grey_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        self.img_shape = self.img.shape

        self.gradient_map = None
        self.binary_map = None

        self.elements = []

    def get_gradient_map(self):
        '''
        :return: gradient map
        '''
        img_f = np.copy(self.grey_img)
        img_f = img_f.astype("float")

        kernel_h = np.array([[0, 0, 0], [0, -1., 1.], [0, 0, 0]])
        kernel_v = np.array([[0, 0, 0], [0, -1., 0], [0, 1., 0]])
        dst1 = abs(cv2.filter2D(img_f, -1, kernel_h))
        dst2 = abs(cv2.filter2D(img_f, -1, kernel_v))
        gradient = (dst1 + dst2).astype('uint8')
        self.gradient_map = gradient
        return gradient

    def get_binary_map(self, min_grad):
        '''
        :param min_grad: if a pixel is bigger than this, then count it as foreground (255)
        :return: binary map
        '''
        if self.gradient_map is None:
            self.get_gradient_map()  # get RoI with high gradient
        rec, bin = cv2.threshold(self.gradient_map, min_grad, 255, cv2.THRESH_BINARY)
        morph = cv2.morphologyEx(bin, cv2.MORPH_CLOSE, (3, 3))  # remove noises
        self.binary_map = morph
        return morph

    def get_elements(self, min_area):
        _, contours, hierarchy = cv2.findContours(bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        for cnt in contours:
            if cv2.contourArea(cnt) > min_area:
                self.elements.append(cnt)

    def visualize_elements(self, color=(255,0,0)):
        board_bin = np.zeros((self.img_shape[0], self.img_shape[0]))
        board_org = self.img.copy()
        cv2.drawContours(board_bin, self.elements, -1, color)
        cv2.drawContours(board_org, self.elements, -1, color)
        cv2.imshow("contour_bin", board_bin)
        cv2.imshow("contour", board_org)
        cv2.waitKey(0)
        cv2.destroyAllWindows()