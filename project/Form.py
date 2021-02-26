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

    def sort_elements(self, direction='h'):
        elements = self.texts + self.rectangles + self.lines
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
