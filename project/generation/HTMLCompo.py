from generation.HTML import HTML
from generation.CSS import CSS


class HTMLCompo:
    def __init__(self, element):
        self.id = element.id
        self.location = element.location    # dictionary {left, right, top, bottom}
        self.element = element      # Element/Table object of detected form element
        self.type = element.type
        self.unit_group_id = element.unit_group_id  # only useful for Vertical_Aligned_Form

        self.parent_block = None    # Block obj
        self.is_section_separator = False

        self.html = None            # HTML obj
        self.html_tag = None
        self.html_class = None
        self.html_id = None
        self.html_script = None     # string

        self.css = {}               # directory of CSS objs, {'.class'/'#id' : CSS obj}
        self.init_html()
        self.init_css()

    def init_html(self):
        if self.type == 'text' or self.type == 'textbox':
            self.html_tag = 'p'
            self.html_id = 'p-'+str(self.element.id)
            self.html = HTML(tag='p', content=self.element.content, id=self.html_id)
        elif self.type == 'table':
            self.html_tag = 'tb'
            self.html_id = 'tb-'+str(self.element.id)
            self.html = HTML(tag='tb', table=self.element, id=self.html_id)
        elif self.type == 'input':
            self.html_tag = 'input'
            self.html_id = 'input-'+str(self.element.id)
            self.html = HTML(tag='input', input=self.element, id=self.html_id)
        elif self.type == 'border':
            self.html_tag = 'div'
            self.html_class = 'border-line'
            self.html = HTML(tag='div', class_name='border-line')
        else:
            self.html_script = ''
            return
        self.html_script = self.html.html_script

    def init_css(self):
        '''
        Only add css led by css ID specific for this compo
        '''
        if self.type == 'text' or self.type == 'textbox':
            css_id = '#p-'+str(self.element.id)
        elif self.type == 'table':
            css_id = '#tb-'+str(self.element.id)
        elif self.type == 'input':
            css_id = '#input-'+str(self.element.id)
        elif self.type == 'border':
            css_id = '#div-' + str(self.element.id)

    def get_input_filling_space(self):
        if self.type != 'input':
            return None
        text_loc = self.element.guide_text.location
        ipt_loc = self.location
        if self.element.is_embedded:
            top_gap = text_loc['top'] - ipt_loc['top']
            bottom_gap = ipt_loc['bottom'] - text_loc['bottom']
            # the text is at the left
            if abs(top_gap - bottom_gap) <= 10:
                blank_space = {'top': ipt_loc['top'], 'bottom': ipt_loc['bottom'], 'left': text_loc['right'] + 5,
                               'right': ipt_loc['right']}
            else:
                # the text is at the upper half
                if top_gap < bottom_gap:
                    blank_space = {'top': text_loc['bottom'], 'left': ipt_loc['left'], 'right': ipt_loc['right'],
                                   'bottom': ipt_loc['bottom']}
                else:
                    blank_space = {'top': ipt_loc['bottom'], 'left': ipt_loc['left'], 'right': ipt_loc['right'],
                                   'bottom': text_loc['top']}
            return [blank_space]
        elif text_loc == ipt_loc:
            blank_space = {'top': text_loc['top'], 'bottom': text_loc['top'], 'left':text_loc['right'], 'right': 2*text_loc['right'] - text_loc['left']}
            return [blank_space]
        elif self.element.is_check_box:
            return [f.location for f in self.element.input_fields]
        else:
            return [f.location for f in self.element.input_fields]

    def get_row_elements_loc_for_table(self):
        '''
        Return a dictionary of all elements locations in a table
        :return: {'element-html-id': {location}}
        '''
        if self.type != 'table':
            return
        ele_locations = {}
        for i, row in enumerate(self.element.rows):
            for j, ele in enumerate(row.elements):
                html_id = self.html_id + '-col-' + str(j) + '-row-' + str(i)
                ele_locations[html_id] = [ele.location]
        return ele_locations
