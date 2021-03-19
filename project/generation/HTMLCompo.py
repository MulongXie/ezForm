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

    def init_HTML(self):
        if self.type == 'text' or self.type == 'textbox':
            self.html_tag = 'p'
        elif self.type == 'table':
            self.html_tag = 'tb'
        elif self.type == 'input':
            self.html_tag = 'input'
        # ignore rectangle and line at this stage
        elif self.type == 'rectangle' or self.type == 'line':
            pass

        self.html = HTML(tag=self.html_tag, id=self.html_id, class_name=self.html_class)
        self.html_script = self.html.html_script
