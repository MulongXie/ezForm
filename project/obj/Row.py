import cv2
from obj.Table import Table


class Row:
    def __init__(self, row_id, elements=None):
        self.row_id = row_id
        self.parent_table = None
        self.location = None

        self.ele_ids = []
        if elements is not None:
            self.elements = elements
            for ele in elements:
                ele.in_row = self
                self.ele_ids.append(ele.id)
            self.sort_elements()
            self.init_bound()
        else:
            self.elements = []

    def init_bound(self):
        left = min([e.location['left'] for e in self.elements])
        top = min([e.location['top'] for e in self.elements])
        right = max([e.location['right'] for e in self.elements])
        bottom = max([e.location['bottom'] for e in self.elements])
        self.location = {'left':left, 'right':right, 'top':top, 'bottom':bottom}

    def sort_elements(self):
        self.elements = sorted(self.elements, key=lambda x: x.location['left'])  # sort from left to right

    def add_element(self, element, reorder=True):
        if element.id in self.ele_ids:
            return
        element.in_row = self
        element.in_table = self.parent_table
        self.elements.append(element)
        self.ele_ids.append(element.id)
        if reorder:
            self.sort_elements()
            self.init_bound()

    def add_elements(self, elements):
        for ele in elements:
            self.add_element(ele, reorder=False)
        self.sort_elements()
        self.init_bound()

    def update_all_elements(self, new_elements):
        self.elements = []
        self.ele_ids = []
        self.add_elements(new_elements)

    def merge_row(self, row):
        for ele in row.elements:
            self.add_element(ele, reorder=False)
        self.sort_elements()
        self.init_bound()
        return self

    def is_empty(self):
        if len(self.elements) == 0:
            return True
        return False

    def add_parent_table(self, table):
        self.parent_table = table
        for ele in self.elements:
            ele.in_table = table

    def match_rows(self, row_b, bias=3):
        '''
        Match tow rows bu checking continuously justified elements
        If matched then extract the matched elements as new rows and return those two new rows
        :param row_b:
        :param bias:
        :return:
        '''
        row_a_eles = self.elements
        row_b_eles = row_b.elements
        for i, re1 in enumerate(row_a_eles):
            for j, re2 in enumerate(row_b_eles):
                # if tow cells from the two rows match, take them as the start points and match forward
                if abs(re1.location['left'] - re2.location['left']) < bias and abs(re1.location['right'] - re2.location['right']) < bias:
                    col_start = [i, j]
                    k = 1
                    while (i + k) < len(row_a_eles) and (j + k) < len(row_b_eles):
                        rek1 = row_a_eles[i + k]
                        rek2 = row_b_eles[j + k]
                        if abs(rek1.location['left'] - rek2.location['left']) < bias and abs(rek1.location['right'] - rek2.location['right']) < bias:
                            k += 1
                        else:
                            break
                    if k > 1:
                        col_end = [i + k, j + k]
                        row_matched_a = Row(elements=row_a_eles[col_start[0]: col_end[0]])
                        row_matched_b = Row(elements=row_b_eles[col_start[1]: col_end[1]])
                        return row_matched_a, row_matched_b
                    else:
                        break
        return None

    def is_matched(self, row_b, bias=3):
        '''
        Match tow rows bu checking continuously justified elements
        Return whether they are matched
        '''
        row_a_eles = self.elements
        row_b_eles = row_b.elements
        for i, re1 in enumerate(row_a_eles):
            for j, re2 in enumerate(row_b_eles):
                # if tow cells from the two rows match, take them as the start points and match forward
                if abs(re1.location['left'] - re2.location['left']) < bias and abs(re1.location['right'] - re2.location['right']) < bias:
                    col_start = [i, j]
                    k = 1
                    while (i + k) < len(row_a_eles) and (j + k) < len(row_b_eles):
                        rek1 = row_a_eles[i + k]
                        rek2 = row_b_eles[j + k]
                        if abs(rek1.location['left'] - rek2.location['left']) < bias and abs(rek1.location['right'] - rek2.location['right']) < bias:
                            k += 1
                        else:
                            break
                    if k > 2:
                        return True
                    else:
                        break
        return False

    def merge_vertical_texts_in_cell(self):
        '''
        For texts vertically interacted in one cell, merge them as a whole
        '''
        texts = []
        non_texts = []
        for ele in self.elements:
            if ele.unit_type == 'text_unit':
                texts.append(ele)
            else:
                non_texts.append(ele)

        changed = True
        while changed:
            changed = False
            temp_set = []
            for text_a in texts:
                merged = False
                for text_b in temp_set:
                    if text_a.is_on_same_line(text_b, 'v', bias_justify=20, bias_gap=10):
                        text_b.merge_text(text_a, direction='v')
                        merged = True
                        changed = True
                        break
                if not merged:
                    temp_set.append(text_a)
            texts = temp_set.copy()

        self.elements = texts + non_texts
        self.sort_elements()

    def visualize_row(self, board, color=(0, 255, 0), line=2, show=False):
        for ele in self.elements:
            ele.visualize_element(board, color=color, line=line)
        if show:
            cv2.imshow('row', board)
            cv2.waitKey()
            cv2.destroyWindow('row')
