from obj.Text import Text
from obj.Image import Image
from obj.Input import Input
import obj.ocr as ocr

import cv2
import time
import numpy as np


class Form:
    def __init__(self, img_file_name):
        self.img_file_name = img_file_name
        self.img = Image(img_file_name)

        # form elements
        self.texts = []         # detected by ocr
        self.rectangles = []    # detected by cv
        self.lines = []         # detected by cv
        self.tables = []        # recognize by grouping rectangles

        # units for input, grouped from the above elements
        self.text_units = []    # text (not in box) + textbox
        self.bar_units = []     # rectangles (not textbox) + lines + tables

        self.inputs = []        # input elements that consists of guide text (text|textbox) and input filed (rectangle|line)

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
        # print('*** Textbox Recognition Time:%.3f s***' % (time.clock() - start))

    def input_unit_recognition(self):
        '''
        Recognize input unit that consists of guide text and input field
        First recognize guide text for input:
            If a text_unit's closet element in alignment is bar_unit, then count it as a guide text
        Second compound the guide text and its bar unit (input field) as an Input element
        '''
        if len(self.text_units) + len(self.bar_units) == 0:
            self.group_elements_to_units()

        units = self.text_units + self.bar_units
        # from left to right
        units = sorted(units, key=lambda x: x.location['left'])
        for i, unit in enumerate(units):
            # board = self.img.img.copy()
            if unit.unit_type == 'text_unit':
                # unit.visualize_element(board, color=(0,0,255))

                for j in range(i+1, len(units)):
                    if not units[j].is_input_part and unit.in_alignment(units[j], direction='h'):
                        if units[j].unit_type == 'bar_unit':
                            unit.is_guide_text = True
                            unit.is_input_part = True
                            units[j].is_input_part = True
                            self.inputs.append(Input(unit, units[j]))
                            # units[j].visualize_element(board, color=(255, 0, 0))
                        else:
                            unit.is_guide_text = False
                        break
                # cv2.imshow('alignment', board)
                # cv2.waitKey()

        # from top to bottom
        units = sorted(units, key=lambda x: x.location['top'])
        for i, unit in enumerate(units):
            board = self.img.img.copy()
            if not unit.is_input_part and unit.unit_type == 'text_unit':
                # unit.visualize_element(board, color=(0, 0, 255))

                for j in range(i + 1, len(units)):
                    if unit.in_alignment(units[j], direction='v'):
                        if not units[j].is_input_part and units[j].unit_type == 'bar_unit':
                            unit.is_guide_text = True
                            unit.is_input_part = True
                            units[j].is_input_part = True
                            self.inputs.append(Input(unit, units[j]))
                            # units[j].visualize_element(board, color=(255, 0, 0))
                        else:
                            unit.is_guide_text = False
                        break
                # cv2.imshow('alignment', board)
                # cv2.waitKey()

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

    def sort_elements(self, direction='left'):
        '''
        :param direction: 'left' or 'top'
        '''
        elements = self.get_all_elements()
        return sorted(elements, key=lambda x: x.location[direction])

    def group_elements_to_units(self):
        '''
        text_units: text (not contained) + textbox
        bar_units: rectangles (not textbox) + lines + tables
        '''
        for text in self.texts:
            if not text.in_box:
                text.unit_type = 'text_unit'
                self.text_units.append(text)
        for ele in self.rectangles + self.lines:
            if ele.type in ('line', 'rectangle'):
                ele.unit_type = 'bar_unit'
                self.bar_units.append(ele)
            elif ele.type == 'textbox':
                ele.unit_type = 'text_unit'
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
        cv2.destroyAllWindows()

    def visualize_inputs(self):
        board = self.img.img.copy()
        for ipt in self.inputs:
            ipt.visualize_element(board, color=(255, 0, 0), line=2)
            # ipt.visualize_input_overlay(board)
        cv2.imshow('Input', board)
        cv2.waitKey()
        cv2.destroyAllWindows()
