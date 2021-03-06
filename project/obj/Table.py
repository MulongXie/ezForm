import cv2


class Table:
    def __init__(self, rows=None):
        self.location = None

        if rows is not None:
            self.rows = rows
            for row in rows:
                row.parent_table = self
            self.sort_rows()
            self.init_bound()
        else:
            self.rows = []

    def init_bound(self):
        left = min([r.location['left'] for r in self.rows])
        top = min([r.location['top'] for r in self.rows])
        right = max([r.location['right'] for r in self.rows])
        bottom = min([r.location['bottom'] for r in self.rows])
        self.location = {'left':left, 'right':right, 'top':top, 'bottom':bottom}

    def sort_rows(self):
        self.rows = sorted(self.rows, key=lambda x: x.location['top'])  # sort from top to bottom

    def add_row(self, row):
        row.parent_table = self
        self.rows.append(row)
        self.sort_rows()
        self.init_bound()

    def add_rows(self, rows):
        for row in rows:
            row.parent_table = self
            self.rows.append(row)
        self.sort_rows()
        self.init_bound()

    def concat_table_by_rows(self, table):
        for row in table.rows:
            self.add_row(row)
        return self

    def is_empty(self):
        if len(self.rows) == 0:
            return True
        return False

    def visualize_table(self, board, color=(0, 255, 0), line=2, show=False):
        for row in self.rows:
            row.visualize_row(board, color=color, line=line)
        if show:
            cv2.imshow('row', board)
            cv2.waitKey()
            cv2.destroyWindow('row')
