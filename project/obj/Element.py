import numpy as np
import cv2


class Element:
    def __init__(self,
                 id=None, type=None, contour=None, location=None, clip_img=None):
        self.id = id
        self.type = type            # text/rectangle/line/textbox
        self.unit_type = None       # text_unit(text or textbox)/bar_unit

        self.contour = contour      # format of findContours
        self.clip_img = clip_img

        self.contains = []          # list of elements that are contained in the element

        self.location = location    # dictionary {left, right, top, bottom}
        self.width = None
        self.height = None
        self.area = None
        self.init_bound()

    '''
    *******************
    *** Basic Bound ***
    *******************
    '''
    def init_bound(self):
        if self.location is not None:
            self.width = self.location['right'] - self.location['left']
            self.height = self.location['bottom'] - self.location['top']
            self.area = self.width * self.height
        else:
            self.get_bound_from_contour()

    def get_bound_from_contour(self):
        if self.contour is not None:
            bound = cv2.boundingRect(self.contour)
            self.width = bound[2]
            self.height = bound[3]
            self.area = self.width * self.height
            self.location = {'left': bound[0], 'top': bound[1], 'right': bound[0] + bound[2], 'bottom': bound[1] + bound[3]}

    def get_clip(self, org_img):
        self.clip_img = org_img[self.location['top']: self.location['bottom'], self.location['left']: self.location['right']]

    '''
    *************************
    *** Shape Recognition ***
    *************************
    '''
    def is_line(self, max_thickness=4):
        if self.height <= max_thickness or self.width <= max_thickness:
            return True
        return False

    def is_rectangle(self):
        '''
        Rectangle recognition by checking slopes between adjacent points
        :param contour: contour
        :return: boolean
        '''
        contour = np.reshape(self.contour, (-1, 2))
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

    '''
    *******************************
    *** Relation with Other Ele ***
    *******************************
    '''
    def element_relation(self, element):
        '''
        Calculate the relation between two elements by iou
        :return:
        -1  : a in b
         0  : a, b are not intersected
         1  : b in a
         2  : a, b are intersected
        '''
        l_a = self.location
        l_b = element.location

        left_in = max(l_a['left'], l_b['left'])
        top_in = max(l_a['top'], l_b['top'])
        right_in = min(l_a['right'], l_b['right'])
        bottom_in = min(l_a['bottom'], l_b['bottom'])

        w_in = max(0, right_in - left_in)
        h_in = max(0, bottom_in - top_in)
        area_in = w_in * h_in
        # area of intersection is 0
        if area_in == 0:
            return 0

        ioa = area_in / self.area
        iob = area_in / element.area

        # print('ioa:%.3f; iob:%.3f' % (ioa, iob))
        # a in b
        if ioa > 0.6:
            return -1
        # b in a
        if iob == 1:
            return 1
        return 2

    def in_alignment(self, ele_b, direction='v', bias=2):
        '''
        Check if the element is in alignment with another
        :param bias: to remove insignificant intersection
        :param direction:
             - 'v': up and down, then check if (a_left <= b_left <= a_right) | (a_left <= b_right <= a_right)
             - 'h': left and right, then check if (a_top <= b_top <= a_bottom) | (a_top <= b_bottom <= a_bottom)
        :return: Boolean that indicate the two are in alignment or not
        '''
        l_a = self.location
        l_b = ele_b.location
        if direction == 'v':
            if max(l_a['left'], l_b['left']) + bias < min(l_a['right'], l_b['right']) - bias:
                # print('In Alignment Vertically')
                return True
        elif direction == 'h':
            if max(l_a['top'], l_b['top']) + bias < min(l_a['bottom'], l_b['bottom']) - bias:
                # print('In Alignment Horizontally')
                return True
        else:
            print("Direction: 'v' or 'h'")
            return
        # print('Not in Alignment')
        return False

    '''
    *********************
    *** Visualization ***
    *********************
    '''
    def visualize_clip(self):
        if self.clip_img is None:
            print('No clip image stored, call get_clip() first')
        cv2.imshow('clip', self.clip_img)
        cv2.waitKey()
        cv2.destroyWindow('clip')

    def visualize_element(self, image, color=None, line=2, show=False):
        if color is None:
            if self.type == 'text':
                color = (255, 0, 0)
            elif self.type == 'rectangle':
                color = (0, 255, 0)
            elif self.type == 'line':
                color = (0, 0, 255)
            elif self.type == 'textbox':
                color = (211, 85, 186)
        cv2.rectangle(image, (self.location['left'], self.location['top']), (self.location['right'], self.location['bottom']), color, line)
        if show:
            cv2.imshow('element', image)
            cv2.waitKey()
            cv2.destroyWindow('element')
