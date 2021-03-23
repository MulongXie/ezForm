import cv2
import numpy as np

from generation.HTML import HTML
from generation.CSS import CSS


class Block:
    def __init__(self, block_id):
        self.block_id = block_id
        self.html_compos = []    # list of HTMLCompos constituting the block
        self.is_abandoned = False

        self.html = None         # HTML object to represent the entire block
        self.html_script = None  # string to represent the HTML script
        self.css = {}            # directory of all CSS objs, {'.class'/'#id' : CSS obj}

        self.init_html()
        self.init_css()

    def init_html(self):
        self.html = HTML(tag='div', id='blk-'+str(self.block_id), class_name='wrap')
        self.html_script = self.html.html_script

    def init_css(self):
        self.css['.wrap'] = CSS(name='.wrap', display='flex', border='1px solid black', margin='5px')

    def add_compo(self, compo):
        compo.parent_block = self
        self.html_compos.append(compo)
        self.html.add_child(compo.html_script)
        self.html_script = self.html.html_script
        self.css.update(compo.css)

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
