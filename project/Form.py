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
            self.texts.append(Text(text['words'], text['location']))
        print('*** OCR Processing Time:%.3f s***' % (time.clock() - start))

    def element_detection(self):
        start = time.clock()
        self.rectangles = self.img.detect_rectangle_elements()
        self.lines = self.img.detect_line_elements()
        print('*** Element Detection Time:%.3f s***' % (time.clock() - start))

    def visualize(self):
        board = self.img.img.copy()
        for text in self.texts:
            loc = text.location
            cv2.rectangle(board, (loc['left'], loc['top']), (loc['left'] + loc['width'], loc['top'] + loc['height']), (255, 0, 0), 1)

        for rec in self.rectangles:
            loc = rec.location
            cv2.rectangle(board, (loc['left'], loc['top']), (loc['right'], loc['bottom']), (0, 255, 0), 1)

        for line in self.lines:
            loc = line.location
            cv2.rectangle(board, (loc['left'], loc['top']), (loc['right'], loc['bottom']), (0, 0, 255), 1)

        cv2.imshow('form', board)
        cv2.waitKey()
        cv2.destroyAllWindows()
