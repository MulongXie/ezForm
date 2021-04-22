class HTML:
    def __init__(self, tag, **kwargs):
        self.tag = tag
        self.attrs = kwargs

        self.class_name = self.init_by_input_attr('class_name')
        self.id = self.init_by_input_attr('id')
        self.style = self.init_by_input_attr('style')
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
            html += ' id="' + self.id + '"'
        if self.class_name is not None:
            html += ' class="' + self.class_name + '"'
        if self.style is not None:
            html += ' style="' + self.style + '"'
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

    def generate_html_p(self, speak=True):
        # start
        html = "<p"
        if self.id is not None:
            html += ' id="' + self.id + '"'
        if self.class_name is not None:
            html += ' class="' + self.class_name + '"'
        if self.style is not None:
            html += ' style="' + self.style + '"'
        html += ">"
        # body
        html += self.content.replace('\n', '</br>')

        # speak
        if speak:
            html += '<button class="speaker" data-target="' + self.id + '" onclick="speak(this)"><span class="glyphicon glyphicon-volume-up"></span></button>'

        # close
        html += "</p>\n"
        self.html_script = html

    def generate_html_input(self, speak=True):
        if self.input.is_check_box:
            self.generate_html_input_checkbox(speak)
        elif self.input.is_embedded:
            self.generate_html_input_embedding(speak)
        else:
            self.generate_html_input_normal(speak)

    def generate_html_input_normal(self, speak=True):
        html = '<div class="input-group">\n'
        # guide text
        html += self.indent() + '<label id="' + 'label-' + self.id + '" class="input-group-addon" for="' + self.id + '">' + self.input.guide_text.content + '</label>\n'
        # input filed
        label_words = [w.lower() for w in self.input.guide_text.content.split(' ')]
        if 'date' in label_words and len(label_words) < 5:
            html += self.indent() + '<input type="date"'
        else:
            html += self.indent() + '<input type="text"'
        if self.id is not None:
            html += ' id="' + self.id + '"'
        if self.class_name is not None:
            html += ' class="form-control ' + self.class_name + '"'
        else:
            html += ' class="form-control"'
        if self.style is not None:
            html += ' style="' + self.style + '"'
        # placeholder
        if self.input.placeholder is not None:
            html += ' placeholder="' + self.input.placeholder + '"'
        html += '>\n'
        # speak
        if speak:
            html += self.indent() + '<div class="input-group-btn">\n'
            html += self.indent(2) + '<button class="speaker btn btn-default" data-target="' + 'label-' + self.id + '" onclick="speak(this)"><span class="glyphicon glyphicon-volume-up"></span></button>\n'
            html += self.indent() + '</div>\n'
        html += '</div>\n'
        self.html_script = html

    def generate_html_input_checkbox(self, speak=True):
        html = '<div class="checkbox">\n'
        html += self.indent() + '<label id="' + 'label-' + self.id + '"><input type="checkbox"'
        # input filed
        if self.id is not None:
            html += ' id="' + self.id + '"'
        if self.class_name is not None:
            html += ' class="' + self.class_name + '"'
        if self.style is not None:
            html += ' style="' + self.style + '"'
        html += '>\n'
        html += self.input.guide_text.content + '</label>\n'
        # speak
        # if speak:
        #     html += self.indent() + '<div class="input-group-btn">\n'
        #     html += self.indent(2) + '<button class="speaker btn btn-default" data-target="' + 'label-' + self.id + '" onclick="speak(this)"><span class="glyphicon glyphicon-volume-up"></span></button>\n'
        #     html += self.indent() + '</div>\n'
        html += '</div>\n'
        self.html_script = html

    def generate_html_input_embedding(self, speak=True):
        html = '<div class="input-group">\n'
        # guide text
        html += self.indent() + '<label id="' + 'label-' + self.id + '" class="input-group-addon" for="' + self.id + '">' + self.input.guide_text.content + '</label>\n'
        # input filed
        label_words = [w.lower() for w in self.input.guide_text.content.split(' ')]
        if 'date' in self.input.guide_text.content.lower() and len(label_words) < 5:
            html += self.indent() + '<input type="date"'
        else:
            html += self.indent() + '<input type="text"'
        if self.id is not None:
            html += ' id="' + self.id + '"'
        if self.class_name is not None:
            html += ' class="form-control ' + self.class_name + '"'
        else:
            html += ' class="form-control"'
        if self.style is not None:
            html += ' style="' + self.style + '"'
        # placeholder
        if self.input.placeholder is not None:
            html += ' placeholder="' + self.input.placeholder + '"'
        html += '>\n'
        # speak
        if speak:
            html += self.indent() + '<div class="input-group-btn">\n'
            html += self.indent(2) + '<button class="speaker btn btn-default" data-target="' + 'label-' + self.id + '" onclick="speak(this)"><span class="glyphicon glyphicon-volume-up"></span></button>\n'
            html += self.indent() + '</div>\n'
        html += '</div>\n'
        self.html_script = html

    def generate_html_table(self):
        heads = [h.content for h in self.table.heading.elements]
        col_num = len(heads)
        html = '<table'
        if self.id is not None:
            html += ' id="' + self.id + '"'
        if self.class_name is not None:
            html += ' class="' + self.class_name + '"'
        if self.style is not None:
            html += ' style="' + self.style + '"'
        html += ">\n"
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

        # add button to insert new row
        html += '<div style="display:block; margin-left:10px; width:80px">\n'
        html += self.indent() + '<button style="width: 80px; height: 40px" onclick="addRow(this)" data-target="' + self.id + '">Add Row</button>\n'
        html += self.indent() + '<button style="width: 80px; height: 40px" onclick="delRow(this)" data-target="' + self.id + '">Delete Row</button>\n'
        html += '</div>\n'

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

    def add_style(self, new_style, is_append=True):
        if is_append and self.style is not None:
            self.style += new_style
        else:
            self.style = new_style
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
