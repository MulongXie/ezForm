import numpy as np
import cv2


class Element:
    def __init__(self,
                 id=None, type=None, contour=None, location=None, clip_img=None):
        self.id = id
        self.is_abandoned = False       # if the element has been merged or defined as noise
        self.type = type                # text/rectangle/line/textbox/border/square
        self.unit_type = None           # text_unit(text or textbox)/bar_unit(rectangle, line or table)
        self.unit_group_id = -1         # only for [Vertical_Aligned_Form], id of groups segmented by separators

        # basic
        self.clip_img = clip_img
        self.contour = contour          # format of findContours
        self.location = location        # dictionary {left, right, top, bottom}
        self.width = None
        self.height = None
        self.area = None
        self.init_bound()

        # for square that is nested in a text
        self.nesting_text = None

        # for character box
        self.is_character_box = False
        self.character_num = 1          # characters the c-box contains
        self.character_area = self.area # area of single character, all cs should be similar

        # for textbox
        self.contains = []              # list of elements that are contained in the element
        self.containment_area = 0
        self.content = None             # for Textbox, the content of text contained

        # for elements in Table and Input
        self.is_module_part = False     # if the element is part of input/table
        self.in_row = None              # Row object, does the element belong to any table row
        self.in_table = None            # Table object, does the element belong to any table
        self.in_input = None            # Input object, if the element is grouped as part of an input element (guide text or input field)

        # neighbour
        self.neighbour_top = None
        self.neighbour_bottom = None
        self.neighbour_left = None
        self.neighbour_right = None

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
    def is_line(self, max_thickness=4, min_length=10):
        if self.height <= max_thickness and self.width >= min_length:
            return True
        return False

    def is_rectangle_or_square(self):
        '''
        Rectangle recognition by checking slopes between adjacent points
        :return: 'rectangle' or 'square' or False
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
        noises = []
        for i, p in enumerate(contour[2:]):
            # calculate the slope k between two neighboor points
            if contour[i][0] == contour[i - 1][0]:
                k = 'v'
            else:
                k = (contour[i][1] - contour[i - 1][1]) / (contour[i][0] - contour[i - 1][0])
            # if test:
            #     print(len(side), k, k_pre, gap_to_pre, len(noises))
            # check if the two points on the same side
            if k != k_pre:
                # leave out noises
                if len(side) < 4:
                    # continue using the last side
                    if len(sides) > 0 and k == slopes[-1] \
                            and not pop_pre and gap_to_pre < 4:
                        side = sides.pop()
                        side += noises
                        side.append(p)
                        k = slopes.pop()
                        pop_pre = True
                        gap_to_pre = 0
                        noises = []
                    # leave out noises
                    else:
                        noises += side
                        gap_to_pre += 1
                        side = [p]
                # count as valid side and store it in sides
                else:
                    side += noises
                    sides.append(side)
                    slopes.append(k_pre)
                    side = [p]
                    pop_pre = False
                    gap_to_pre = 0
                    noises = []
                k_pre = k
            else:
                side.append(p)
        # concatenate with the first side if same slope
        if len(slopes) > 0 and k_pre == slopes[0]:
            sides[0] += side
        elif len(side) >= 4:
            sides.append(side)
            slopes.append(k_pre)
        lens = [len(s) for s in sides]
        # if test:
        # print('Side Number:', len(sides), ' Side Lengths:', lens, ' Side Slopes:', slopes)
        if len(sides) != 4:
            return False
        # if it's rectangle, the opposite sides pair should be similar
        max_diff1 = 0.1 * max(lens[0], lens[2]) if lens[0] > 100 or lens[2] > 100 else 6
        max_diff2 = 0.1 * max(lens[1], lens[3]) if lens[1] > 100 or lens[3] > 100 else 6
        if (abs(lens[0] - lens[2]) < max_diff1) and (abs(lens[1] - lens[3]) < max_diff2):
            # check if the rectangle is square
            is_square = True
            for i in range(1, len(lens)):
                if abs(lens[0] - lens[i]) >= 10:
                    is_square = False
                    break
            if is_square:
                return 'square'
            else:
                return 'rectangle'
        return False

    '''
    *******************************
    *** Relation with Other Ele ***
    *******************************
    '''
    def calc_intersection(self, element, bias=0, board=None):
        '''
        :return: ioa(self) and iob(the element)
        '''
        l_a = self.location
        l_b = element.location
        left_in = max(l_a['left'], l_b['left']) + bias
        top_in = max(l_a['top'], l_b['top']) + bias
        right_in = min(l_a['right'], l_b['right'])
        bottom_in = min(l_a['bottom'], l_b['bottom'])

        w_in = max(0, right_in - left_in)
        h_in = max(0, bottom_in - top_in)
        area_in = w_in * h_in
        ioa = area_in / self.area
        iob = area_in / element.area

        if board is not None and ioa != 0:
            print('ioa:%.3f; iob:%.3f' % (ioa, iob))
            element.visualize_element(board)
            self.visualize_element(board, show=True)

        return ioa, iob

    def pos_relation(self, element, bias=0, board=None):
        '''
        Calculate the relation between two elements by iou
        :return:
        -1  : a in b
         0  : a, b are not intersected
         1  : b in a
         2  : a, b are intersected
        '''
        ioa, iob = self.calc_intersection(element, bias, board)
        # area of intersection is 0
        if ioa == 0:
            return 0
        # a in b
        if ioa > 0.6:
            return -1
        # b in a
        if iob == 1:
            return 1
        return 2

    def is_in_alignment(self, ele_b, direction='v', bias=4):
        '''
        Check if the element is in alignment with another
        :param bias: to remove insignificant intersection
        :param direction:
             - 'v': vertical up-down alignment
             - 'h': horizontal left-right alignment
        :return: Boolean that indicate the two are in alignment or not
        '''
        l_a = self.location
        l_b = ele_b.location
        if direction == 'v':
            if max(l_a['left'], l_b['left']) + bias < min(l_a['right'], l_b['right']):
                # print('In Alignment Vertically')
                return True
        elif direction == 'h':
            if max(l_a['top'], l_b['top']) + bias < min(l_a['bottom'], l_b['bottom']):
                # print('In Alignment Horizontally')
                return True
        # print('Not in Alignment')
        return False

    def is_justified(self, ele_b, direction='h', max_bias_justify=4):
        '''
        Check if the element is justified
        :param max_bias_justify: maximum bias if two elements to be justified
        :param direction:
             - 'v': vertical up-down connection
             - 'h': horizontal left-right connection
        '''
        l_a = self.location
        l_b = ele_b.location
        # connected vertically - up and below
        if direction == 'v':
            # left and right should be justified
            if abs(l_a['left'] - l_b['left']) < max_bias_justify and abs(l_a['right'] - l_b['right']) < max_bias_justify:
                return True
            return False
        elif direction == 'h':
            # top and bottom should be justified
            if abs(l_a['top'] - l_b['top']) < max_bias_justify and abs(l_a['bottom'] - l_b['bottom']) < max_bias_justify:
                return True
            return False

    def is_on_same_line(self, ele_b, direction='h', bias_gap=4, bias_justify=4):
        '''
        Check if the element is on the same row(direction='h') or column(direction='v') with ele_b
        :param direction:
             - 'v': vertical up-down connection
             - 'h': horizontal left-right connection
        :return:
        '''
        l_a = self.location
        l_b = ele_b.location
        # connected vertically - up and below
        if direction == 'v':
            # left and right should be justified
            if self.is_justified(ele_b, direction='v', max_bias_justify=bias_justify):
                # top and bottom should be connected (small gap)
                if abs(l_a['bottom'] - l_b['top']) < bias_gap or abs(l_a['top'] - l_b['bottom']) < bias_gap:
                    return True
            return False
        elif direction == 'h':
            # top and bottom should be justified
            if self.is_justified(ele_b, direction='h', max_bias_justify=bias_justify):
                # top and bottom should be connected (small gap)
                if abs(l_a['right'] - l_b['left']) < bias_gap or abs(l_a['left'] - l_b['right']) < bias_gap:
                    return True
            return False

    def merge_ele(self, ele_b):
        ele_a = self
        ele_b.is_abandoned = True

        top = min(ele_a.location['top'], ele_b.location['top'])
        left = min(ele_a.location['left'], ele_b.location['left'])
        right = max(ele_a.location['right'], ele_b.location['right'])
        bottom = max(ele_a.location['bottom'], ele_b.location['bottom'])
        self.location = {'left': left, 'top': top, 'right': right, 'bottom': bottom}
        self.width = self.location['right'] - self.location['left']
        self.height = self.location['bottom'] - self.location['top']
        self.area = self.width * self.height

    '''
    *************************
    *** For character box ***
    *************************
    '''
    def is_in_same_character_box(self, ele):
        if self.type not in ('rectangle', 'square') or ele.type not in ('rectangle', 'square'):
            return False
        if max(self.character_area, ele.character_area) / min(self.character_area, ele.character_area) < 1.2 and \
                (self.is_on_same_line(ele, direction='h', bias_gap=10) or self.pos_relation(ele) != 0):
            return True
        return False

    def character_box_merge_ele(self, ele):
        self.merge_ele(ele)
        self.is_character_box = True
        self.character_num += 1
        self.character_area = int((self.character_area + ele.character_area) / 2)
        # character box cannot be 'square'
        if self.type == 'square':
            self.type = 'rectangle'

    '''
    ********************
    *** For text box ***
    ********************
    '''
    def is_textbox_or_border(self):
        '''
        If a rectangle contains only texts in it, then label the rect as type of 'textbox'
        Else if it contains other rectangles in it, then label it as type of 'border'
        '''
        if len(self.contains) == 0 or self.is_character_box:
            return False
        # remove noise
        if self.type == 'square' and len(self.contains) == 1 and self.containment_area / self.area > 0.6:
            # print(self.contains[0].type)
            self.contains[0].is_abandoned = True
            return False

        for ele in self.contains:
            if ele.type != 'text':
                self.type = 'border'
                return 'border'
        self.type = 'textbox'
        return 'textbox'

    def textbox_merge_and_extract_texts_content(self, v_max_merged_gap=10):
        '''
        For Textbox, extract the text content
        '''
        texts = self.contains
        changed = True
        while changed:
            changed = False
            temp_set = []
            for text_a in texts:
                merged = False
                for text_b in temp_set:
                    if text_a.is_in_alignment(text_b, direction='v', bias=0) and \
                            max(text_a.location['top'], text_b.location['top']) - min(text_a.location['bottom'], text_b.location['bottom']) < v_max_merged_gap:
                        text_b.merge_text(text_a)
                        merged = True
                        changed = True
                        break
                if not merged:
                    temp_set.append(text_a)
            texts = temp_set.copy()

        self.contains = texts
        self.containment_area = sum([c.area for c in self.contains])
        self.content = '\n'.join([t.content for t in texts])

    def merge_text(self, text_b, direction='h'):
        text_a = self
        self.merge_ele(text_b)

        if direction == 'h':
            if text_a.location['left'] < text_b.location['left']:
                left_element = text_a
                right_element = text_b
            else:
                left_element = text_b
                right_element = text_a
            self.content = left_element.content + ' ' + right_element.content
        elif direction == 'v':
            if text_a.location['top'] < text_b.location['top']:
                top_element = text_a
                bottom_element = text_b
            else:
                top_element = text_b
                bottom_element = text_a
            self.content = top_element.content + '\n' + bottom_element.content

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
            if self.type == 'text' or self.type == 'textbox':
                color = (255, 0, 0)
            elif self.type == 'rectangle':
                color = (0, 255, 0)
            elif self.type == 'line':
                color = (211, 85, 186)
            elif self.type == 'border':
                color = (168, 168, 0)
            elif self.type == 'square':
                color = (0, 168, 168)
            else:
                print('Not a shape')
                color = (0, 0, 255)
        cv2.rectangle(image, (self.location['left'], self.location['top']), (self.location['right'], self.location['bottom']), color, line)
        if show:
            cv2.imshow('element', image)
            cv2.waitKey()
            cv2.destroyWindow('element')

    def visualize_element_contour(self, image):
        img_shape = image.shape
        board = np.zeros((img_shape[0], img_shape[1]))
        cv2.drawContours(board, [self.contour], -1, 255)
        cv2.imshow('element-cnt', board)
        cv2.waitKey()
        cv2.destroyWindow('element-cnt')

