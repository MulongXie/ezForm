import cv2
import numpy as np


class Block:
    def __init__(self, block_id):
        self.block_id = block_id
        self.html_compos = []   # list of HTMLCompos constituting the block
        self.is_abandoned = False

    def add_compo(self, compo):
        compo.parent_block = self
        self.html_compos.append(compo)

    def add_compos(self, compos):
        for compo in compos:
            self.add_compo(compo)

    def merge_block(self, block):
        self.add_compos(block.html_compos)
        block.html_compos = []
        block.is_abandoned = True

    def visualize_block(self, board):
        for compo in self.html_compos:
            compo.element.visualize_element(board)
        cv2.imshow('block', board)
        cv2.waitKey()
        cv2.destroyWindow('block')
