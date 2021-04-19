import cv2


class Table:
    def __init__(self, table_id, rows=None):
        self.id = table_id
        self.type = 'table'
        self.location = None
        self.width = None
        self.height = None

        self.unit_group_id = -1   # only for [Vertical_Aligned_Form], if of groups segmented by separators

        self.row_ids = []
        if rows is not None:
            self.rows = rows
            self.unit_group_id = rows[0].unit_group_id
            for row in rows:
                row.add_parent_table(self)
                self.row_ids.append(row.row_id)
            self.sort_rows()
            self.init_bound()
        else:
            self.rows = []            # List of Row objects
        self.heading = None           # Row object
        self.columns = []             # List of lists of Element objects, use a list of Element objects to rep a column

    def init_bound(self):
        left = min([r.location['left'] for r in self.rows])
        top = min([r.location['top'] for r in self.rows])
        right = max([r.location['right'] for r in self.rows])
        bottom = max([r.location['bottom'] for r in self.rows])
        self.location = {'left':left, 'right':right, 'top':top, 'bottom':bottom}
        self.width = self.location['right'] - self.location['left']
        self.height = self.location['bottom'] - self.location['top']

    def sort_rows(self):
        self.rows = sorted(self.rows, key=lambda x: x.location['top'])  # sort from top to bottom

    def is_empty(self):
        if len(self.rows) == 0:
            return True
        return False

    def add_row(self, row, reorder=True):
        if row.row_id in self.row_ids:
            return
        if self.unit_group_id == -1:
            self.unit_group_id = row.unit_group_id
        row.add_parent_table(self)
        self.rows.append(row)
        self.row_ids.append(row.row_id)
        if reorder:
            self.sort_rows()
            self.init_bound()

    def add_rows(self, rows):
        for row in rows:
            self.add_row(row, reorder=False)
        self.sort_rows()
        self.init_bound()

    def add_heading(self, heading):
        for head in heading.elements:
            head.is_module_part = True
        self.heading = heading
        self.add_row(heading)

    def merge_table(self, table):
        for row in table.rows:
            self.add_row(row, reorder=False)
        self.sort_rows()
        self.init_bound()
        return self

    def is_in_alignment(self, ele_b, direction='v', bias=4):
        '''
        Check if the element is in alignment with another
        :param bias: to remove insignificant intersection
        :param direction:
             - 'v': vertical up-down alignment
             - 'h': horizontal left-right alignment
        :return: Boolean that indicate the two are in alignment or not
        '''
        bias = min(bias, min(self.width, ele_b.width) - 1)
        l_a = self.location
        l_b = ele_b.location
        if direction == 'v':
            if max(l_a['left'], l_b['left']) + bias < min(l_a['right'], l_b['right']):
                return True
        elif direction == 'h':
            if max(l_a['top'], l_b['top']) + bias < min(l_a['bottom'], l_b['bottom']):
                return True
        return False

    def merge_vertical_texts_in_cell(self):
        for row in self.rows:
            row.merge_vertical_texts_in_cell()

    def is_ele_contained_in_table(self, element, bias=4):
        '''
        Check if the element is contained in the table
        '''
        l_a = self.location
        l_e = element.location
        if l_a['left'] - bias < l_e['left'] and l_a['right'] + bias > l_e['right'] and\
            l_a['top'] - bias < l_e['top'] and l_a['bottom'] + bias > l_e['bottom']:
            return True
        return False

    def insert_element(self, element):
        '''
        Insert element into the table, find a most matched row to store it
        :param element: the element should be contained in the table
        '''
        for row in self.rows:
            if element.is_in_alignment(row, direction='h', bias=1):
                row.add_element(element)
                self.sort_rows()
                self.init_bound()
                return

    def split_columns(self):
        '''
        Spilt columns according to the heading
        Column: A list of Element objects
        '''
        if self.heading is not None:
            for head in self.heading.elements:
                col = [head]
                max_bias_justify = int(head.width / 2)
                for row in self.rows[1:]:
                    for ele in row.elements:
                        if not ele.is_module_part:
                            if head.is_justified(ele, direction='v', max_bias_justify=max_bias_justify) or\
                                    (head.location['left'] - max_bias_justify / 2 < ele.location['left'] and head.location['right'] + max_bias_justify / 2> ele.location['right']) or\
                                    (ele.location['left'] - max_bias_justify / 2 < head.location['left'] and ele.location['right'] + max_bias_justify / 2> head.location['right']):
                                ele.is_module_part = True
                                col.append(ele)
                                break
                self.columns.append(col)

    def rm_noisy_element(self):
        '''
        Remove all invalid elements that are not in some columns
        '''
        for row in self.rows[1:]:
            valid_eles = []
            for ele in row.elements:
                if ele.is_module_part:
                    valid_eles.append(ele)
                else:
                    ele.is_abandoned = True
            row.update_all_elements(valid_eles)

    def visualize_columns(self, board):
        for col in self.columns:
            b = board.copy()
            for ele in col:
                ele.visualize_element(b)
            cv2.imshow('col', b)
            cv2.waitKey()
            cv2.destroyWindow('col')

    def visualize_element(self, board, color=(255, 255, 0), line=2, show=False):
        for row in self.rows:
            row.visualize_row(board, color=color, line=line)
        cv2.rectangle(board, (self.location['left'], self.location['top']), (self.location['right'], self.location['bottom']), color, line)
        if show:
            cv2.imshow('row', board)
            cv2.waitKey()
            cv2.destroyWindow('row')
