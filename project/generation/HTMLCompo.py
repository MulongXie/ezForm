from generation.HTML import HTML


class HTMLCompo:
    def __init__(self, element):
        self.element = element      # Element/Table object of detected form element
        self.type = element.type

        self.html_tag = None
        self.html_class = None
        self.html_id = None

        self.html = None
        self.html_script = None

        self.init_HTML()

    def init_HTML(self):
        if self.type == 'text' or self.type == 'textbox':
            self.html_tag = 'p'
            self.html = HTML(tag='p', content=self.element.content)
        elif self.type == 'table':
            self.html_tag = 'tb'
            self.html = HTML(tag='tb', heading=self.element.heading)
        elif self.type == 'input':
            self.html_tag = 'input'
            self.html = HTML(tag='input', guide_text=self.element.guide_text)
        # ignore rectangle and line at this stage
        elif self.type == 'rectangle' or self.type == 'line':
            self.html_tag = 'div'
            self.html = HTML(tag='div')

        self.html_script = self.html.html_script
