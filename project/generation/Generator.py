from detection.Form import Form
from generation.Page import Page
from generation.HTML import HTML
from generation.HTMLCompo import HTMLCompo
from generation.Block import Block

import os


class Generator:
    def __init__(self, form):
        self.form = form
        self.compos = form.get_detection_result()
        self.reassign_compo_id()

        self.blocks = []        # list of Block objs to group compos
        self.block_id = 0
        self.html_compos = []   # list of HTMLCompos objs
        self.page = None

    def reassign_compo_id(self):
        id = 0
        for c in self.compos:
            c.id = id
            id += 1

    def init_html_compos(self):
        for compo in self.compos:
            self.html_compos.append(HTMLCompo(compo))
        self.html_compos = sorted(self.html_compos, key=lambda x: x.location['top'])

    def init_page_html(self):
        if self.page is None:
            self.page = Page()
        for block in self.blocks:
            self.page.add_compo_html(block.html)

    def init_page_css(self):
        if self.page is None:
            self.page = Page()
        for block in self.blocks:
            self.page.add_compo_css(block.css)

    def slice_blocks(self):
        '''
        Slice blocks according to horizontal alignment
        '''
        compos = self.html_compos
        for i in range(len(compos)):
            for j in range(i + 1, len(compos)):
                if compos[i].location['bottom'] < compos[j].location['top']:
                    break
                # group elements in same horizontal alignment into same block
                if compos[i].element.is_in_alignment(compos[j], direction='h', bias=2):
                    if compos[i].parent_block is not None and compos[j].parent_block is not None:
                        if compos[i].parent_block.block_id != compos[j].parent_block.block_id:
                            compos[i].parent_block.merge_block(compos[j].parent_block)
                        else:
                            continue

                    elif compos[i].parent_block is None and compos[j].parent_block is None:
                        block = Block(self.block_id)
                        self.block_id += 1
                        self.blocks.append(block)
                        block.add_compos([compos[i], compos[j]])

                    elif compos[i].parent_block is not None and compos[j].parent_block is None:
                        block = compos[i].parent_block
                        block.add_compo(compos[j])
            if compos[i].parent_block is None:
                block = Block(self.block_id)
                self.block_id += 1
                self.blocks.append(block)
                block.add_compo(compos[i])

    def export_page(self, export_dir='data/output/', html_file_name='xml.html', css_file_name='xml.css'):
        return self.page.export(directory=export_dir, html_file_name=html_file_name, css_file_name=css_file_name)

    def visualize_blocks(self, img):
        for blk in self.blocks:
            board = img.copy()
            blk.visualize_block(board)
