from Component import Component
from Text import Text
import ocr
import ip

import cv2


class Form:
    def __init__(self, img_file_name):
        self.img_file_name = img_file_name
        self.img = cv2.imread(img_file_name)

        self.text_compos = []
        self.nt_compos = []

    def ocr_detection(self):
        detection_result = ocr.ocr_detection(self.img_file_name)
        texts = detection_result['words_result']
        for text in texts:
            self.text_compos.append(Text(text['words'], text['location']))

    def filling_area_detection(self):
        pass

    def visualize_texts(self, color=(255,0,0)):
        board = self.img.copy()
        for text in self.text_compos:
            loc = text.location
            cv2.rectangle(board, (loc['left'], loc['top']), (loc['left'] + loc['width'], loc['top'] + loc['height']), color, 1)
        cv2.imshow('texts', board)
        cv2.waitKey()
        cv2.destroyAllWindows()