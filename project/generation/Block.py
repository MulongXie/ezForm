import cv2
import numpy as np

from generation.HTML import HTML
from generation.CSS import CSS


class Block:
    def __init__(self, block_id, is_section_wrapper=False):
        self.block_id = block_id
        self.html_compos = []    # list of HTMLCompos constituting the block

        self.is_abandoned = False  # set True if the block is merged into others

        self.is_section_title = False    # if the block is section title
        self.is_section_wrapper = is_section_wrapper  # if the block is section wrapper
        self.children_blocks = []        # for section wrapper, list of Block objs contained by it
        self.parent_section = None  # section wrapper Block obj that contains the block

        self.html = None         # HTML object to represent the entire block
        self.html_script = None  # string to represent the HTML script
        self.css = {}            # directory of all CSS objs, {'.class'/'#id' : CSS obj}

        self.init_html()
        self.init_css()

    def init_html(self):
        self.html = HTML(tag='div', id='blk-'+str(self.block_id), class_name='wrap-center')
        if self.is_section_wrapper:
            self.html.change_class('section-wrapper', is_append=True)
        self.html_script = self.html.html_script

    def init_css(self):
        self.css['.wrap-center'] = CSS(name='.wrap-center', display='flex', border='1px solid black', margin='5px', justify_content='center')
        if self.is_section_wrapper:
            self.css['.section-wrapper'] = CSS(name='.wrap-center', display='flex', border='1px solid black', margin='5px')

    def sort_compos(self, by='left'):
        self.html_compos = sorted(self.html_compos, key=lambda x: x.location[by])

    def add_compo(self, compo):
        compo.parent_block = self
        self.css.update(compo.css)
        # set vertical alignment for input compounds
        if compo.type == 'input' and '.wrap-center' in self.css:
            self.css.pop('.wrap-center')
            self.html.change_class('wrap-vertical', is_append=False)
            self.css['.wrap-vertical'] = CSS(name='.wrap-vertical', border='1px solid black', margin='5px')

        # if one of the compo is section separator, set the block as section
        if compo.is_section_separator:
            self.is_section_title = True
            self.html.change_class('section-title', is_append=True)

        self.html_compos.append(compo)
        self.sort_compos()
        self.html.update_children([c.html_script for c in self.html_compos])
        self.html_script = self.html.html_script

    def add_compos(self, compos):
        for compo in compos:
            self.add_compo(compo)

    def add_child_block(self, block):
        if block not in self.children_blocks:
            block.parent_section = self
            self.children_blocks.append(block)

        self.css.update(block.css)
        self.html.update_children([b.html_script for b in self.children_blocks])
        self.html_script = self.html.html_script

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
