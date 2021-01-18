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

        self.all_elements_contour = []
        self.rectangle_elements_contour = []
        self.line_elements_contour = []

    '''
    **** Pre-processing ****
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
    **** Element Detection ****
    '''
    def get_elements_contour(self, min_area=100):
        if self.binary_map is None:
            self.get_binary_map()
        _, contours, hierarchy = cv2.findContours(self.binary_map, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        for cnt in contours:
            if cv2.contourArea(cnt) > min_area:
                self.all_elements_contour.append(cnt)
        return self.all_elements_contour

    def detect_rectangle_elements(self):
        def is_rectangle(contour):
            '''
            Rectangle recognition by checking slopes between adjacent points
            :param contour: contour
            :return: boolean
            '''
            contour = np.reshape(contour, (-1, 2))
            # calculate the slope k (y2-y1)/(x2-x1) the first between two neighboor points
            if contour[0][0] == contour[1][0]:
                k_pre = 'v'
            else:
                k_pre = (contour[0][1] - contour[1][1]) / (contour[0][0] - contour[1][0])

            sides = []
            slopes = []
            side = [contour[0], contour[1]]
            # variables for checking if it's valid to continue using the previous side
            pop_pre = False
            gap_to_pre = 0
            for i, p in enumerate(contour[2:]):
                # calculate the slope k between two neighboor points
                if contour[i][0] == contour[i - 1][0]:
                    k = 'v'
                else:
                    k = (contour[i][1] - contour[i - 1][1]) / (contour[i][0] - contour[i - 1][0])
                # print(side, k_pre, gap_to_pre)
                # check if the two points on the same side
                if k != k_pre:
                    # leave out noises
                    if len(side) < 4:
                        # continue using the last side
                        if len(sides) > 0 and k == slopes[-1] \
                                and not pop_pre and gap_to_pre < 4:
                            side = sides.pop()
                            side.append(p)
                            k = slopes.pop()
                            pop_pre = True
                            gap_to_pre = 0
                        # leave out noises
                        else:
                            gap_to_pre += 1
                            side = [p]
                    # count as valid side and store it in sides
                    else:
                        sides.append(side)
                        slopes.append(k_pre)
                        side = [p]
                        pop_pre = False
                        gap_to_pre = 0
                    k_pre = k
                else:
                    side.append(p)
            sides.append(side)
            slopes.append(k_pre)
            if len(sides) != 4:
                return False
            # print('Side Number:', len(sides))
            lens = [len(s) for s in sides]
            # print('Side Lengths:', lens, ' Side Slopes:', slopes)
            if (abs(lens[0] - lens[2]) < 4) and (abs(lens[1] - lens[3]) < 4):
                return True
            return False

        if len(self.all_elements_contour) == 0:
            self.get_elements_contour()
        for cnt in self.all_elements_contour:
            if is_rectangle(cnt):
                self.rectangle_elements_contour.append(cnt)
        return self.rectangle_elements_contour

    def visualize_elements_contours(self, element_opt='all', board_opt='org',
                                    contours=None, window_name='contour', color=(255, 0, 0)):
        '''
        :param element_opt: 'all'/'rectangle'/'line'
        :param board_opt: 'org'/'binary'
        :param contours: input contours, if none, check element_opt and use inner elements
        :return: drawn image
        '''
        if contours is None:
            if element_opt == 'all':
                contours = self.all_elements_contour
            elif element_opt == 'rectangle':
                contours = self.rectangle_elements_contour
            elif element_opt == 'line':
                contours = self.line_elements_contour
            else:
                print("element_opt: 'all'/'rectangle'/'line'")
                return
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
