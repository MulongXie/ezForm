from obj.Element import Element

import numpy as np
import cv2


# Input element consisting of two parts(units): guide text & input field (rectangle or line)
class Input(Element):
    def __init__(self, guide_text, input_field):
        self.guide_text = guide_text       # text/textbox
        self.input_field = input_field      # rectangle/line
        super().__init__()

    def init_bound(self):
        '''
        Compound two units to get the bound of Input
        '''
        loc_t = self.guide_text.location
        loc_f = self.input_field.location
        left = min(loc_t['left'], loc_f['left'])
        right = max(loc_t['right'], loc_f['right'])
        top = min(loc_t['top'], loc_f['top'])
        bottom = max(loc_t['bottom'], loc_f['bottom'])

        self.location = {'left': left, 'right': right, 'top': top, 'bottom': bottom}
        self.width = right - left
        self.height = bottom - top
        self.area = self.width * self.height

    def visualize_input_overlay(self, image, show=False):
        mask = np.zeros(image.shape, dtype=np.uint8)
        cv2.rectangle(mask, (self.location['left'], self.location['top']), (self.location['right'], self.location['bottom']), (0,255,0), -1)
        cv2.rectangle(mask, (self.location['left'], self.location['top']), (self.location['right'], self.location['bottom']), (0,0,255), 2)
        cv2.addWeighted(image, 1, mask, 1, 0, image)
        if show:
            cv2.imshow('Input element', image)
            cv2.waitKey()
