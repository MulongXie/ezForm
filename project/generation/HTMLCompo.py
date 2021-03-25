from generation.HTML import HTML
from generation.CSS import CSS


class HTMLCompo:
    def __init__(self, element):
        self.id = element.id
        self.location = element.location    # dictionary {left, right, top, bottom}
        self.element = element      # Element/Table object of detected form element
        self.type = element.type

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
            self.html = HTML(tag='p', content=self.element.content, id='p-'+str(self.element.id))
        elif self.type == 'table':
            self.html_tag = 'tb'
            self.html = HTML(tag='tb', table=self.element, id='tb-'+str(self.element.id))
        elif self.type == 'input':
            self.html_tag = 'input'
            self.html = HTML(tag='input', input=self.element, id='input-'+str(self.element.id))
        # ignore rectangle and line at this stage
        elif self.type == 'rectangle' or self.type == 'line':
            self.html_tag = 'div'
            self.html = HTML(tag='div', class_name='border-line')

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
        elif self.type == 'rectangle' or self.type == 'line':
            css_id = '#div-' + str(self.element.id)
