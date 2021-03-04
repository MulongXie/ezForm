import cv2


class Row:
    def __init__(self, elements=None):
        self.elements = elements if elements is not None else []
        self.parent_table = None

    def add_element(self, element):
        element.in_row = self
        self.elements.append(element)
        self.elements = sorted(self.elements, key=lambda x: x.location['left'])

    def concat_row(self, row):
        for ele in row.elements:
            self.add_element(ele)
        return self

    def row_similarity(self, row_b):
        pass

    def visualize_row(self, board, color=(0, 255, 0), line=2, show=False):
        for ele in self.elements:
            ele.visualize_element(board, color=color, line=line)
        if show:
            cv2.imshow('row', board)
            cv2.waitKey()
            cv2.destroyWindow('row')
