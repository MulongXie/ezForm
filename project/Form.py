from Text import Text
from Image import Image
import ocr

import cv2
import time


class Form:
    def __init__(self, img_file_name):
        self.img_file_name = img_file_name
        self.img = Image(img_file_name)

        self.texts = []
        self.rectangles = []
        self.lines = []
        self.tables = []

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

    def textbox_detection(self):
        '''
        If a rectangle contains only one text in it, then recategorize the rect as type of 'textbox'
        '''
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
            if rec.contains == 1:
                rec.type = 'textbox'
                rec.contains[0].in_box = True

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

    def visualize_all_elements(self):
        board = self.img.img.copy()
        for text in self.texts:
            text.visualize_element(board, color=(255, 0, 0))

        for rec in self.rectangles:
            rec.visualize_element(board, color=(0, 255, 0))

        for line in self.lines:
            line.visualize_element(board, color=(0, 0, 255))

        cv2.imshow('form', board)
        cv2.waitKey()
        cv2.destroyAllWindows()
