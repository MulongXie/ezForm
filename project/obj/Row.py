import cv2
from obj.Table import Table


class Row:
    def __init__(self, elements=None):
        self.parent_table = None
        self.location = None

        if elements is not None:
            self.elements = elements
            for ele in elements:
                ele.in_row = self
            self.sort_elements()
            self.init_bound()
        else:
            self.elements = []

    def init_bound(self):
        left = min([e.location['left'] for e in self.elements])
        top = min([e.location['top'] for e in self.elements])
        right = max([e.location['right'] for e in self.elements])
        bottom = min([e.location['bottom'] for e in self.elements])
        self.location = {'left':left, 'right':right, 'top':top, 'bottom':bottom}

    def sort_elements(self):
        self.elements = sorted(self.elements, key=lambda x: x.location['left'])  # sort from left to right

    def add_element(self, element):
        element.in_row = self
        self.elements.append(element)
        self.sort_elements()
        self.init_bound()

    def concat_row(self, row):
        for ele in row.elements:
            self.add_element(ele)
        return self

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

    def visualize_row(self, board, color=(0, 255, 0), line=2, show=False):
        for ele in self.elements:
            ele.visualize_element(board, color=color, line=line)
        if show:
            cv2.imshow('row', board)
            cv2.waitKey()
            cv2.destroyWindow('row')
