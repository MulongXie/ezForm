from Component import Component
from Text import Text
import ocr

import cv2


class Form:
    def __init__(self, img_file_name=None):
        self.img_file_name = img_file_name
        self.img = cv2.imread(img_file_name) if img_file_name is not None else None

        self.text_compos = []
        self.nt_compos = []

    def OCR_detection(self):
        if self.img_file_name is None:
            print('No image of form is given')
        else:
            detection_result = ocr.ocr_detection(self.img_file_name)
            texts = detection_result['words_result']
            for text in texts:
                self.text_compos.append(Text(text['words'], text['location']))