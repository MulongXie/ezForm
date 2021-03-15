import cv2


class Table:
    def __init__(self, table_id, rows=None):
        self.table_id = table_id
        self.location = None

        self.row_ids = []
        if rows is not None:
            self.rows = rows
            for row in rows:
                row.add_parent_table(self)
                self.row_ids.append(row.row_id)
            self.sort_rows()
            self.init_bound()
        else:
            self.rows = []

    def init_bound(self):
        left = min([r.location['left'] for r in self.rows])
        top = min([r.location['top'] for r in self.rows])
        right = max([r.location['right'] for r in self.rows])
        bottom = max([r.location['bottom'] for r in self.rows])
        self.location = {'left':left, 'right':right, 'top':top, 'bottom':bottom}

    def sort_rows(self):
        self.rows = sorted(self.rows, key=lambda x: x.location['top'])  # sort from top to bottom

    def add_row(self, row, reorder=True):
        if row.row_id in self.row_ids:
            return
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

    def merge_table(self, table):
        for row in table.rows:
            self.add_row(row, reorder=False)
        self.sort_rows()
        self.init_bound()
        return self

    def is_empty(self):
        if len(self.rows) == 0:
            return True
        return False

    def is_ele_contained_in_table(self, element, bias=2):
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
            if element.is_in_alignment(row):
                row.add_element(element)

    def visualize_table(self, board, color=(0, 255, 0), line=2, show=False):
        for row in self.rows:
            row.visualize_row(board, color=color, line=line)
        cv2.rectangle(board, (self.location['left'], self.location['top']), (self.location['right'], self.location['bottom']), color, line)
        if show:
            cv2.imshow('row', board)
            cv2.waitKey()
            cv2.destroyWindow('row')
