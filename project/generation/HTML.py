class HTML:
    def __init__(self, tag, **kwargs):
        self.tag = tag
        self.attrs = kwargs

        self.class_name = self.init_by_input_attr('class_name')
        self.id = self.init_by_input_attr('id')
        self.children = self.init_by_input_attr('children', [])  # list of string, html script
        self.close = True

        self.html_script = None

        self.content = self.init_by_input_attr('content', '')    # text content for [p]
        self.table = self.init_by_input_attr('table')            # Table obj for [tb]
        self.input = self.init_by_input_attr('input')            # Input obj for [input]

        self.init_html()

    def init_by_input_attr(self, attr, non_exist_alt=None):
        if attr in self.attrs:
            return self.attrs[attr]
        return non_exist_alt

    def init_html(self):
        if self.tag == 'tb':
            self.generate_html_table()
        elif self.tag == 'input':
            self.generate_html_input()
        elif self.tag == 'p':
            self.generate_html_p()
        else:
            self.generate_html()

    def generate_html(self):
        # start
        html = "<" + self.tag
        if self.id is not None:
            html += " id=\"" + self.id + "\""
        if self.class_name is not None:
            html += " class=\"" + self.class_name + "\""
        html += ">\n"
        # body
        for child in self.children:
            # indent
            child = '\t' + child.replace('\n', '\n\t')
            html += child[:-1]
        # close
        if self.close:
            html += "</" + self.tag + ">\n"
        else:
            html[-1] = '/>\n'
        self.html_script = html

    def generate_html_p(self):
        # start
        html = "<p"
        if self.id is not None:
            html += " id=\"" + self.id + "\""
        if self.class_name is not None:
            html += " class=\"" + self.class_name + "\""
        html += ">"
        # body
        html += self.content.replace('\n', '</br>')
        # close
        html += "</p>\n"
        self.html_script = html

    def generate_html_input(self):
        # guide text
        html = '<label for="' + self.id + '">' + self.input.guide_text.content + '</label>\n'
        # input filed
        html += '<input type="text" id="' + self.id + '"><br>\n'
        self.html_script = html

    def generate_html_table(self):
        heads = [h.content for h in self.table.heading.elements]
        col_num = len(heads)
        html = '<table id="' + self.id + '">\n'
        # heading
        thead = self.indent() + '<thead>\n' + self.indent(2) + '<tr>\n'
        for h in heads:
            thead += self.indent(3) + '<th>' + h + '</th>\n'
        thead += self.indent(2) + '</tr>\n'

        # body
        tbody = self.indent() + '<tbody>\n' + self.indent(2) + '<tr>\n'
        for i in range(col_num):
            tbody += self.indent(3) + '<td><input id="' + self.id + '-col-' + str(i) + '-row-1"></td>\n'
        tbody += self.indent(2) + '</tr>\n'

        html += thead + tbody + '</table>\n'
        self.html_script = html

    def add_child(self, child):
        '''
        :param child: string, html script
        '''
        self.children.append(child)
        self.init_html()

    def update_children(self, children):
        '''
        Replace all children with new ones
        :param children: list of string of html script
        '''
        self.children = children
        self.init_html()

    def add_class(self, new_class, is_append=True):
        if is_append and self.class_name is not None:
            if new_class not in self.class_name:
                self.class_name = self.class_name + ' ' + new_class
        else:
            self.class_name = new_class
        self.init_html()

    def del_class(self, class_name):
        self.class_name = self.class_name.replace(class_name, '')
        if self.class_name == '':
            return
        if self.class_name[0] == ' ':
            self.class_name = self.class_name[1:]
        if self.class_name[-1] == ' ':
            self.class_name = self.class_name[:-1]

    def indent(self, indent_num=1):
        indent = ''
        for i in range(indent_num):
            indent += '\t'
        return indent
