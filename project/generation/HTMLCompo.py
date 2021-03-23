from generation.HTML import HTML
from generation.CSS import CSS


class HTMLCompo:
    def __init__(self, element):
        self.id = element.id
        self.location = element.location    # dictionary {left, right, top, bottom}
        self.element = element      # Element/Table object of detected form element
        self.type = element.type

        self.parent_block = None    # Block obj

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
        if self.type == 'text' or self.type == 'textbox':
            id = '.p-'+str(self.element.id)
            self.css['p'] = CSS(name='p', margin='5px')
        elif self.type == 'table':
            id = '.tb-'+str(self.element.id)
            self.css['table'] = CSS(name='table', width='100%', border='1px solid black')
            self.css['th'] = CSS(name='th', border='1px solid black')
            self.css['td'] = CSS(name='td', border='1px solid black', height='20px')
        elif self.type == 'input':
            id = '.input-'+str(self.element.id)
            self.css['input'] = CSS(name='input', margin='5px')
            self.css['label'] = CSS(name='label', margin='5px')
        elif self.type == 'rectangle' or self.type == 'line':
            id = '.div-' + str(self.element.id)
            self.css['.border-line'] = CSS(name='.border-line')
