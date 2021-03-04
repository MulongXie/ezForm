from obj.Text import Text
from obj.Image import Image
from obj.Input import Input
from obj.Table import Table
from obj.Row import Row
import obj.ocr as ocr

import cv2
import time
import numpy as np


class Form:
    def __init__(self, img_file_name):
        self.img_file_name = img_file_name
        self.img = Image(img_file_name)

        # form elements
        self.texts = []             # detected by ocr
        self.rectangles = []        # detected by cv
        self.lines = []             # detected by cv
        self.tables = []            # recognize by grouping rectangles

        # units for input, grouped from the above elements
        self.text_units = []    # text (not in box) + textbox
        self.bar_units = []     # rectangles (not textbox) + lines + tables
        self.all_units = []

        self.sorted_left_unit = []
        self.sorted_top_unit = []

        self.inputs = []        # input elements that consists of guide text (text|textbox) and input filed (rectangle|line)

    '''
    **************************
    *** Element Processing ***
    **************************
    '''
    def get_all_elements(self):
        return self.texts + self.rectangles + self.lines + self.tables

    def assign_element_ids(self):
        '''
        Assign an unique id to each element and store the id mapping
        '''
        for i, ele in enumerate(self.get_all_elements()):
            ele.id = i

    def sort_units(self):
        '''
        Sort all units by left and top respectively, and store the result in id lists
        '''
        self.sorted_left_unit = sorted(self.all_units, key=lambda x: x.location['left'])
        self.sorted_top_unit = sorted(self.all_units, key=lambda x: x.location['top'])

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
        self.all_units = self.text_units + self.bar_units

    def find_neighbour_unit(self, unit, direction='right', bias=3):
        '''
        Find the first unit next to and in alignment with the target
        :param direction:
            -> right: find right neighbour
            -> below: find below neighbour
        :return:
        '''
        if direction == 'right':
            # check is there any connected unit on the right
            for u in self.sorted_left_unit:
                # find the first one one the left if they are neighbours
                if u.id != unit.id and u.location['left'] + bias >= unit.location['right']:
                    # the tow should be justified
                    if unit.is_in_alignment(u, direction='h'):
                        return u
        elif direction == 'below':
            # check is there any connected unit on the right
            for u in self.sorted_top_unit:
                # pass those on the left
                if u.id != unit.id and u.location['top'] + bias >= unit.location['bottom']:
                    # the tow should be justified if they are neighbours
                    if unit.is_in_alignment(u, direction='v'):
                        return u
        return None

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
                relation = text.pos_relation(rec)
                # if text.pos_relation(rec) != 0:
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

    def input_compound_recognition(self):
        '''
        Recognize input unit that consists of [guide text] and [input field]
        First recognize guide text for input:
            If a text_unit's closet element in alignment is bar_unit, then count it as a guide text
        Second compound the guide text and its bar unit (input field) as an Input element
        '''
        if len(self.text_units) + len(self.bar_units) == 0:
            self.group_elements_to_units()
        if len(self.sorted_left_unit) + len(self.sorted_top_unit) == 0:
            self.sort_units()

        # from left to right
        units = self.sorted_left_unit
        for i, unit in enumerate(units):
            # board = self.img.img.copy()
            if unit.unit_type == 'text_unit':
                # unit.visualize_element(board, color=(0,0,255))

                for j in range(i+1, len(units)):
                    if not units[j].is_input_part and unit.is_in_alignment(units[j], direction='h'):
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
        units = self.sorted_top_unit
        for i, unit in enumerate(units):
            board = self.img.img.copy()
            if not unit.is_input_part and unit.unit_type == 'text_unit':
                # unit.visualize_element(board, color=(0, 0, 255))

                for j in range(i + 1, len(units)):
                    if unit.is_in_alignment(units[j], direction='v'):
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

    def row_detection(self, unit):
        '''
        Detect row through grouping all left-right connected and justified elements
        :param unit: start unit
        '''
        row = Row()
        neighbour_right = self.find_neighbour_unit(unit, 'right')
        is_row = False
        # if there is a connected neighbour, add it and the current unit to a Row
        while neighbour_right is not None and unit.is_connected(neighbour_right, 'h'):
            row.add_element(unit)
            # if the neighbour is already in a row, then simply add the current one to the row
            if neighbour_right.in_row is not None:
                row.concat_row(neighbour_right.in_row)
                break

            is_row = True
            unit = neighbour_right
            neighbour_right = self.find_neighbour_unit(neighbour_right, 'right')
        if is_row:
            row.add_element(unit)
        return row


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
