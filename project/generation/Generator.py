from detection.Form import Form
from generation.Page import Page
from generation.HTML import HTML
from generation.HTMLCompo import HTMLCompo
from generation.Block import Block

import os
import json
import cv2


class Generator:
    def __init__(self, form):
        self.form = form
        self.form_name = form.form_name
        self.compos = form.get_detection_result()
        self.reassign_compo_id()

        self.blocks = []        # list of Block objs to group compos
        self.block_id = 0
        self.sections = []
        self.html_compos = []   # list of HTMLCompos objs
        self.page = None

        # only useful for Vertical_Aligned_Form
        self.html_compos_groups = {}  # {'group_id': [list of html_compos]}

        self.export_dir = 'data/output/' + self.form_name
        os.makedirs(self.export_dir, exist_ok=True)

    def reassign_compo_id(self):
        id = 0
        for c in self.compos:
            c.id = id
            id += 1

    def group_html_compos_by_unit_group_id(self):
        groups = {}
        for compo in self.html_compos:
            # print(compo.unit_group_id)
            g_id = compo.unit_group_id
            if g_id in groups:
                groups[g_id].append(compo)
            else:
                groups[g_id] = [compo]
        self.html_compos_groups = groups

    def init_html_compos(self):
        for compo in self.compos:
            self.html_compos.append(HTMLCompo(compo))
        self.html_compos = sorted(self.html_compos, key=lambda x: x.location['top'])

        self.section_separator_recognition()

    def init_page(self, by='section'):
        if self.page is None:
            self.page = Page()
        if by == 'block':
            for block in self.blocks:
                self.page.add_compo_html(block.html)
                self.page.add_compo_css(block.css)
        elif by == 'section':
            for sect in self.sections:
                self.page.add_compo_html(sect.html)
                self.page.add_compo_css(sect.css)

    def section_separator_recognition(self):
        keywords = {'part', 'section'}
        for compo in self.html_compos:
            if compo.type == 'text':
                if compo.type == 'text' or compo.type == 'textbox':
                    # if the first three words include the keywords
                    words = set(compo.element.content.lower().split()[:3])
                    inters = keywords.intersection(words)
                    if len(inters) > 0:
                        compo.is_section_separator = True

    def slice_block_by_group(self):
        section_wrapper = Block(self.block_id, is_section_wrapper=True, is_first_section=True)
        self.sections.append(section_wrapper)
        for gid in self.html_compos_groups:
            compos = self.html_compos_groups[gid]
            section_wrapper = self.slice_blocks(compos, section_wrapper)

    def slice_blocks(self, compos, prev_section_wrapper):
        '''
        Slice blocks according to horizontal alignment
        '''
        section_wrapper = prev_section_wrapper
        self.block_id += 1

        for i in range(len(compos)):
            block_updated = False
            for j in range(i + 1, len(compos)):
                if compos[i].location['bottom'] < compos[j].location['top']:
                    break
                # group elements in same horizontal alignment into same block
                if compos[i].element.is_in_alignment(compos[j], direction='h', bias=2):
                    # merge blocks if both i and j has been grouped in parent blocks
                    if compos[i].parent_block is not None and compos[j].parent_block is not None:
                        if compos[i].parent_block.block_id != compos[j].parent_block.block_id:
                            compos[i].parent_block.merge_block(compos[j].parent_block)
                        else:
                            continue
                    # if no compo has parent block, creat a new one
                    elif compos[i].parent_block is None and compos[j].parent_block is None:
                        block = Block(self.block_id)
                        self.block_id += 1
                        self.blocks.append(block)
                        block.add_compos([compos[i], compos[j]])
                    # else add the ungrouped one to existing block
                    elif compos[i].parent_block is not None and compos[j].parent_block is None:
                        block = compos[i].parent_block
                        block.add_compo(compos[j])
                    elif compos[i].parent_block is None and compos[j].parent_block is not None:
                        block = compos[j].parent_block
                        block.add_compo(compos[i])
                    # indicate the block is changed
                    block_updated = True
            # if i is not grouped, create a block for itself
            if compos[i].parent_block is None:
                block = Block(self.block_id)
                self.block_id += 1
                self.blocks.append(block)
                block.add_compo(compos[i])
                block_updated = True

            if block_updated:
                # create a new section if the block is a section title
                if compos[i].parent_block.is_section_title:
                    section_wrapper = Block(self.block_id, is_section_wrapper=True)
                    section_wrapper.add_child_block(compos[i].parent_block)
                    self.block_id += 1
                    self.sections.append(section_wrapper)
                # add the block to current section
                else:
                    section_wrapper.add_child_block(compos[i].parent_block)
        return section_wrapper

    def export_input_fields_locations(self):
        fields = {}  # {input html id: [list of fields locations]}
        for compo in self.html_compos:
            if compo.type == 'input':
                fields[compo.html_id] = [f.location for f in compo.element.input_fields]
            elif compo.type == 'table':
                fields.update(compo.get_row_elements_loc_for_table())
        json.dump(fields, open(os.path.join(self.export_dir, 'input_loc.json'), 'w'), indent=4)
        return fields

    def export_page(self, html_file_name='xml.html', css_file_name='xml.css'):
        self.export_input_fields_locations()
        return self.page.export(directory=self.export_dir, html_file_name=html_file_name, css_file_name=css_file_name)

    def visualize_compos_groups(self):
        groups = self.html_compos_groups
        for k in groups:
            group = groups[k]
            board = self.form.get_img_copy()
            for compo in group:
                compo.element.visualize_element(board)
            cv2.imshow('group', board)
            cv2.waitKey()
            cv2.destroyAllWindows()

    def visualize_blocks(self):
        for blk in self.blocks:
            board = self.form.get_img_copy()
            blk.visualize_block(board)

    def visualize_sections(self):
        for sect in self.sections:
            board = self.form.get_img_copy()
            sect.visualize_block(board)
