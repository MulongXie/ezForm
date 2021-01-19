import cv2
import numpy as np

from Element import Element


class Image:
    def __init__(self, img_file_name):
        self.img_file_name = img_file_name
        self.img = cv2.imread(img_file_name)
        self.grey_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        self.img_shape = self.img.shape

        self.gradient_map = None
        self.binary_map = None

        self.all_elements = []
        self.rectangle_elements = []
        self.line_elements = []

    '''
    ************************
    **** Pre-processing ****
    ************************
    '''
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

    def get_binary_map(self, min_grad=2):
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

    '''
    ***************************
    **** Element Detection ****
    ***************************
    '''
    def get_elements(self, min_area=100):
        '''
        get all elements on the image by findContours
        :return: list of [Component]
        '''
        if self.binary_map is None:
            self.get_binary_map()
        _, contours, hierarchy = cv2.findContours(self.binary_map, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        for cnt in contours:
            if cv2.contourArea(cnt) > min_area:
                self.all_elements.append(Element(contour=cnt))
        return self.all_elements

    def detect_rectangle_elements(self):
        if len(self.all_elements) == 0:
            self.get_elements()
        for ele in self.all_elements:
            if ele.is_rectangle():
                ele.type = 'rectangle'
                self.rectangle_elements.append(ele)
        return self.rectangle_elements

    def detect_line_elements(self):
        if len(self.all_elements) == 0:
            self.get_elements()
        for ele in self.all_elements:
            if ele.is_line():
                ele.type = 'line'
                self.line_elements.append(ele)
        return self.line_elements

    '''
    ***********************
    **** Visualization ****
    ***********************
    '''

    def visualize_elements_contours(self, element_opt='all', board_opt='org',
                                    contours=None, board=None,
                                    window_name='contour', color=(255, 0, 0)):
        '''
        :param element_opt: 'all'/'rectangle'/'line'
        :param board_opt: 'org'/'binary'
        :param contours: input contours, if none, check element_opt and use inner elements
        :param board: board image to draw on
        :return: drawn image
        '''
        if contours is None:
            if element_opt == 'all':
                contours = [ele.contour for ele in self.all_elements]
            elif element_opt == 'rectangle':
                contours = [ele.contour for ele in self.rectangle_elements]
            elif element_opt == 'line':
                contours = [ele.contour for ele in self.line_elements]
            else:
                print("element_opt: 'all'/'rectangle'/'line'")
                return
        if board is None:
            if board_opt == 'org':
                board = self.img.copy()
            elif board_opt == 'binary':
                board = np.zeros((self.img_shape[0], self.img_shape[1]))
            else:
                print("board_opt: 'org'/'binary'")
                return
        cv2.drawContours(board, contours, -1, color)
        cv2.imshow(window_name, board)
        cv2.waitKey()
        cv2.destroyWindow(window_name)
        return board
