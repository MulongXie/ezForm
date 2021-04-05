from detection.Element import Element

import numpy as np
import cv2


# Input element consisting of two parts(units): guide text & input field (rectangle or line)
class Input(Element):
    def __init__(self, guide_text, input_field, is_embedded=False, placeholder=None):
        guide_text.in_input = self
        guide_text.is_guide_text = True
        guide_text.is_module_part = True
        input_field.in_input = self
        input_field.is_module_part = True

        self.is_embedded = is_embedded   # indicate if the guide text and input filed in the same box

        self.guide_text = guide_text                    # text/textbox element
        self.input_fields = [input_field]               # list of rectangle/line elements
        self.fields_location = input_field.location
        self.placeholder = placeholder  # string
        if self.placeholder is None and len(guide_text.content.split(':')) > 1:
            self.placeholder = guide_text.content.split(':')[1]

        super().__init__(type='input')
        self.unit_group_id = guide_text.unit_group_id   # only for [Vertical_Aligned_Form], if of groups segmented by separators

    def init_bound(self):
        '''
        Compound two units to get the bound of Input
        '''
        loc_t = self.guide_text.location
        loc_f = self.fields_location
        left = min(loc_t['left'], loc_f['left'])
        right = max(loc_t['right'], loc_f['right'])
        top = min(loc_t['top'], loc_f['top'])
        bottom = max(loc_t['bottom'], loc_f['bottom'])

        self.location = {'left': left, 'right': right, 'top': top, 'bottom': bottom}
        self.width = right - left
        self.height = bottom - top
        self.area = self.width * self.height

    def is_connected_field(self, bar):
        '''
        Check if the bar is part of the input field
        '''
        for f in self.input_fields:
            if f.unit_group_id == bar.unit_group_id and\
                    (f.is_on_same_line(bar, direction='v', bias_gap=4, bias_justify=4) or
                     f.is_on_same_line(bar, direction='h', bias_gap=2, bias_justify=4)):
                return True
        return False

    def merge_guide_text(self, text):
        self.guide_text.merge_text(text, direction='v')
        self.init_bound()

    def merge_input_field(self, field):
        field.is_module_part = True
        self.input_fields.append(field)
        top = min(self.fields_location['top'], field.location['top'])
        left = min(self.fields_location['left'], field.location['left'])
        right = max(self.fields_location['right'], field.location['right'])
        bottom = max(self.fields_location['bottom'], field.location['bottom'])
        self.fields_location = {'left': left, 'top': top, 'right': right, 'bottom': bottom}
        self.init_bound()

    def visualize_input_overlay(self, image, show=False):
        mask = np.zeros(image.shape, dtype=np.uint8)
        cv2.rectangle(mask, (self.location['left'], self.location['top']), (self.location['right'], self.location['bottom']), (0,255,0), -1)
        cv2.rectangle(mask, (self.location['left'], self.location['top']), (self.location['right'], self.location['bottom']), (0,0,255), 2)
        cv2.addWeighted(image, 1, mask, 1, 0, image)
        if show:
            cv2.imshow('Input element', image)
            cv2.waitKey()
