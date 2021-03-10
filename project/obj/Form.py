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
        self.sorted_right_unit = []
        self.sorted_top_unit = []
        self.sorted_bottom_unit = []

        self.inputs = []        # input elements that consists of guide text (text|textbox) and input filed (rectangle|line)

        self.row_id = 0
        self.table_id = 0

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
        self.sorted_right_unit = self.sorted_left_unit.copy()
        self.sorted_right_unit.reverse()

        self.sorted_top_unit = sorted(self.all_units, key=lambda x: x.location['top'])
        self.sorted_bottom_unit = self.sorted_top_unit.copy()
        self.sorted_bottom_unit.reverse()

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
            if ele.in_table is not None:
                continue
            if ele.type in ('line', 'rectangle'):
                ele.unit_type = 'bar_unit'
                self.bar_units.append(ele)
            elif ele.type == 'textbox':
                ele.unit_type = 'text_unit'
                self.text_units.append(ele)
        self.all_units = self.text_units + self.bar_units

    def find_neighbour_unit(self, unit, direction='right', bias=4):
        '''
        Find the first unit next to and in alignment with the target
        :param direction:
            -> left: find left neighbour
            -> right: find right neighbour
            -> top: find top neighbour
            -> below: find below neighbour
        :return:
        '''
        if direction == 'right':
            if unit.neighbour_right is not None:
                return unit.neighbour_right
            # check is there any connected unit on the right
            for u in self.sorted_left_unit:
                if u.id != unit.id and u.location['left'] + bias >= unit.location['right']:
                    # the tow should be justified
                    if unit.is_in_alignment(u, direction='h'):
                        unit.neighbour_right = u
                        u.neighbour_left = unit
                        return u
        elif direction == 'left':
            if unit.neighbour_left is not None:
                return unit.neighbour_left
            # check is there any connected unit on the left
            for u in self.sorted_right_unit:
                if u.id != unit.id and unit.location['left'] + bias >= u.location['right']:
                    # the tow should be justified
                    if unit.is_in_alignment(u, direction='h'):
                        unit.neighbour_left = u
                        u.neighbour_right = unit
                        return u
        elif direction == 'below':
            if unit.neighbour_bottom is not None:
                return unit.neighbour_bottom
            # check is there any connected unit below
            for u in self.sorted_top_unit:
                if u.id != unit.id and u.location['top'] + bias >= unit.location['bottom']:
                    # the tow should be justified if they are neighbours
                    if unit.is_in_alignment(u, direction='v'):
                        unit.neighbour_bottom = u
                        u.neighbour_top = unit
                        return u
        elif direction == 'top':
            if unit.neighbour_top is not None:
                return unit.neighbour_top
            # check is there any connected unit above
            for u in self.sorted_bottom_unit:
                if u.id != unit.id and unit.location['top'] + bias >= u.location['bottom']:
                    # the tow should be justified if they are neighbours
                    if unit.is_in_alignment(u, direction='v'):
                        unit.neighbour_top = u
                        u.neighbour_bottom = unit
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
                    if units[j].in_input is None and units[j].in_table is None and\
                            unit.is_in_alignment(units[j], direction='h'):
                        # if the text unit is connected and justified with a bar unit, then form them as an input object
                        if units[j].unit_type == 'bar_unit':
                            unit.is_guide_text = True
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
            # board = self.img.img.copy()
            if unit.in_input is None and unit.unit_type == 'text_unit':
                # unit.visualize_element(board, color=(0, 0, 255))

                for j in range(i + 1, len(units)):
                    if unit.is_in_alignment(units[j], direction='v'):
                        # if the text unit is connected and justified with a bar unit, then form them as an input object
                        if units[j].in_input is None and units[j].in_table is None and\
                                units[j].unit_type == 'bar_unit':
                            unit.is_guide_text = True
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
        # if already are detected in a row
        if unit.in_row is not None:
            return unit.in_row
        unit_org = unit

        row = Row(self.row_id)
        self.row_id += 1
        # right forward
        neighbour_right = self.find_neighbour_unit(unit, 'right')
        is_row = False
        # if there is a connected neighbour, add it and the current unit to a Row
        while neighbour_right is not None and unit.is_on_same_line(neighbour_right, 'h')\
                and (neighbour_right.type == 'rectangle' and neighbour_right.unit_type == 'bar_unit'):
            if not is_row:
                row.add_element(unit)
                is_row = True
            # if the neighbour is already in a row, then simply add the current one to the row
            if neighbour_right.in_row is not None:
                row.merge_row(neighbour_right.in_row)
                break
            row.add_element(neighbour_right)
            unit = neighbour_right
            neighbour_right = self.find_neighbour_unit(neighbour_right, 'right')

        # left forward
        unit = unit_org
        neighbour_left = self.find_neighbour_unit(unit, 'left')
        # if there is neighbour on the same row, add it and the current unit to a Row
        while neighbour_left is not None and unit.is_on_same_line(neighbour_left, 'h')\
                and (neighbour_left.type == 'rectangle' and neighbour_left.unit_type == 'bar_unit'):
            if not is_row:
                row.add_element(unit)
                is_row = True
            # if the neighbour is already in a row, then simply add the current one to the row
            if neighbour_left.in_row is not None:
                row.merge_row(neighbour_left.in_row)
                break
            row.add_element(neighbour_left)
            unit = neighbour_left
            neighbour_left = self.find_neighbour_unit(neighbour_left, 'left')

        if len(row.elements) > 1:
            # row.visualize_row(self.img.img.copy(), show=True)
            return row
        else:
            return None

    def table_detection(self):
        recorded_row_ids = []
        recorded_table_ids = []
        for unit in self.all_units:
            if unit.type == 'rectangle' and unit.unit_type == 'bar_unit':
                # if an element has right(same row) and below(same column) connected elements
                # then check if its row and the row below it are matched
                row = self.row_detection(unit)
                if row is not None:
                    # avoid redundancy
                    if row.row_id in recorded_row_ids:
                        continue
                    else:
                        recorded_row_ids.append(row.row_id)

                    if row.parent_table is not None:
                        if row.parent_table.table_id in recorded_table_ids:
                            continue
                        table = row.parent_table
                    else:
                        table = Table(self.table_id)
                        recorded_table_ids.append(self.table_id)
                        self.table_id += 1

                    # *** detect down forwards ***
                    unit_a = unit
                    unit_b = self.find_neighbour_unit(unit_a, 'below')
                    if unit_b.type != 'rectangle' or unit_b.unit_type != 'bar_unit':
                        continue
                    row_a = row
                    # check if the unit has neighbour on the same colunm
                    while unit_a.is_on_same_line(unit_b, direction='v'):
                        row_b = self.row_detection(unit_b)
                        # check if its row and the row below it matches
                        # merge matched parts of the two rows to a table
                        if row_b is not None and row_a.is_matched(row_b):
                            if row_b.parent_table is not None:
                                table.merge_table(row_b.parent_table)
                            else:
                                if table.is_empty():
                                    table.add_rows([row_a, row_b])
                                else:
                                    table.add_row(row_b)
                            unit_a = unit_b
                            row_a = row_b
                            unit_b = self.find_neighbour_unit(unit_a, 'below')
                        else:
                            break

                    # *** detect up forwards ***
                    unit_a = unit
                    unit_b = self.find_neighbour_unit(unit_a, 'top')
                    if unit_b.type != 'rectangle' or unit_b.unit_type != 'bar_unit':
                        continue
                    row_a = row
                    # check if the unit has neighbour on the same colunm
                    while unit_a.is_on_same_line(unit_b, direction='v'):
                        row_b = self.row_detection(unit_b)
                        # check if its row and the row below it matches
                        # merge matched parts of the two rows to a table
                        if row_b is not None and row_a.is_matched(row_b):
                            if row_b.parent_table is not None:
                                table.merge_table(row_b.parent_table)
                            else:
                                if table.is_empty():
                                    table.add_rows([row_a, row_b])
                                else:
                                    table.add_row(row_b)
                            unit_a = unit_b
                            row_a = row_b
                            unit_b = self.find_neighbour_unit(unit_a, 'top')
                        else:
                            break

                    if not table.is_empty():
                        board = self.get_img_copy()
                        table.visualize_table(board)
                        unit.visualize_element(board, color=(0,0,255), show=True)
                        self.tables.append(table)
        return self.tables

    '''
    *********************
    *** Visualization ***
    *********************
    '''
    def get_img_copy(self):
        return self.img.img.copy()

    def visualize_all_elements(self):
        board = self.get_img_copy()
        for text in self.texts:
            if not text.in_box:
                text.visualize_element(board)

        for rec in self.rectangles:
            rec.visualize_element(board)

        for line in self.lines:
            line.visualize_element(board)

        for table in self.tables:
            table.visualize_table(board, color=(255,255,0))

        cv2.imshow('form', board)
        cv2.waitKey()
        cv2.destroyAllWindows()

    def visualize_units(self):
        board = self.get_img_copy()
        for text_unit in self.text_units:
            text_unit.visualize_element(board, color=(0, 255, 0))
        for bar_unit in self.bar_units:
            bar_unit.visualize_element(board, color=(255, 0, 0))
        cv2.imshow('Units', board)
        cv2.waitKey()
        cv2.destroyAllWindows()

    def visualize_inputs(self):
        board = self.get_img_copy()
        for ipt in self.inputs:
            ipt.visualize_element(board, color=(255, 0, 0), line=2)
            # ipt.visualize_input_overlay(board)
        cv2.imshow('Input', board)
        cv2.waitKey()
        cv2.destroyAllWindows()
