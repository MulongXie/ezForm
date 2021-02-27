from Text import Text
from Image import Image
import ocr

import cv2
import time


class Form:
    def __init__(self, img_file_name):
        self.img_file_name = img_file_name
        self.img = Image(img_file_name)

        # form elements
        self.texts = []         # detected by ocr
        self.rectangles = []    # detected by cv
        self.lines = []         # detected by cv
        self.tables = []        # recognize by grouping rectangles

        # units for input bar, grouped from the above elements
        self.text_units = []    # text (not contained) + textbox
        self.bar_units = []     # rectangles (not textbox) + lines + tables

    '''
    *************************
    *** Element Detection ***
    *************************
    '''
    def text_detection(self):
        start = time.clock()
        detection_result = ocr.ocr_detection(self.img_file_name)
        texts = detection_result['words_result']
        for text in texts:
            location = {'left': text['location']['left'], 'top': text['location']['top'],
                        'right': text['location']['left'] + text['location']['width'],
                        'bottom': text['location']['top'] + text['location']['height']}
            self.texts.append(Text(text['words'], location))
        print('*** OCR Processing Time:%.3f s***' % (time.clock() - start))

    def element_detection(self):
        start = time.clock()
        self.rectangles = self.img.detect_rectangle_elements()
        self.lines = self.img.detect_line_elements()
        print('*** Element Detection Time:%.3f s***' % (time.clock() - start))

    def textbox_recognition(self):
        '''
        If a rectangle contains only one text in it, then recategorize the rect as type of 'textbox'
        '''
        start = time.clock()
        # iteratively check the relationship between texts and rectangles
        for text in self.texts:
            board = self.img.img.copy()
            for rec in self.rectangles:
                relation = text.element_relation(rec)
                # if text.element_relation(rec) != 0:
                #     text.visualize_element(board, (0, 255, 0), 2)
                #     rec.visualize_element(board, (0, 0, 255), 2, show=True)

                # if the text is contained in the rectangle box
                if relation == -1:
                    # text.visualize_element(board, (0, 255, 0), 2)
                    # rec.visualize_element(board, (0, 0, 255), 2, show=True)
                    rec.contains.append(text)

        # if the rectangle contains only one text, label it as type of textbox
        for rec in self.rectangles:
            if len(rec.contains) == 1:
                rec.type = 'textbox'
                rec.contains[0].in_box = True
        print('*** Element Detection Time:%.3f s***' % (time.clock() - start))

    def guideword_recognition(self):
        '''
        Recognize guide words for input unit
        '''

    '''
    **************************
    *** Element Processing ***
    **************************
    '''
    def get_all_elements(self):
        return self.texts + self.rectangles + self.lines + self.tables

    def assign_ele_ids(self):
        for i, ele in enumerate(self.get_all_elements()):
            ele.id = i

    def sort_elements(self, direction='h'):
        elements = self.get_all_elements()
        # horizontally
        if direction == 'h':
            return sorted(elements, key=lambda x: x.location['top'])
        elif direction == 'v':
            return sorted(elements, key=lambda x: x.location['left'])

    def group_elements_to_units(self):
        '''
        text_units: text (not contained) + textbox
        bar_units: rectangles (not textbox) + lines + tables
        '''
        for text in self.texts:
            if not text.in_box:
                self.text_units.append(text)

        for ele in self.rectangles + self.lines:
            if ele.type in ('line', 'rectangle'):
                self.bar_units.append(ele)
            elif ele.type == 'textbox':
                self.text_units.append(ele)

    '''
    *********************
    *** Visualization ***
    *********************
    '''
    def visualize_all_elements(self):
        board = self.img.img.copy()
        for text in self.texts:
            if not text.in_box:
                text.visualize_element(board)

        for rec in self.rectangles:
            rec.visualize_element(board)

        for line in self.lines:
            line.visualize_element(board)

        cv2.imshow('form', board)
        cv2.waitKey()
        cv2.destroyAllWindows()

    def visualize_units(self):
        board = self.img.img.copy()
        for text_unit in self.text_units:
            text_unit.visualize_element(board, color=(0, 255, 0))
        for bar_unit in self.bar_units:
            bar_unit.visualize_element(board, color=(255, 0, 0))
        cv2.imshow('tidied', board)
        cv2.waitKey()
