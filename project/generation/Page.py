import os


class Page:
    def __init__(self, title='Title', html_file_name='xml.html', css_file_name='xml.css'):
        self.html_file_name = html_file_name
        self.css_file_name = css_file_name

        self.compos_html = []   # list of HTML objs
        self.compos_css = {}    # directory of CSS objs, {'.class'/'#id' : CSS obj}

        self.title = title
        self.html_header = None
        self.html_body = None
        self.html_end = "</body>\n</html>"

        self.html_script = ''
        self.css_script = ''
        self.init_page_html()
        self.init_page_css()

    def init_page_html(self):
        # header
        self.html_header = "<!DOCTYPE html>\n<html>\n<head>\n\t<title>" \
                           + self.title + "</title>\n" \
                           + "<link rel=\"stylesheet\" href=\"" + self.css_file_name + "\">" \
                           + "</head>\n"
        # body
        self.html_body = "<body>\n"
        for html in self.compos_html:
            self.html_body += html.html_script
        # assembly
        self.html_script = self.html_header + self.html_body + self.html_end

    def init_page_css(self):
        self.css_script = 'ul{\n\tlist-style: None;\n\tpadding: 0;\n\tmargin:0;\n}\n'
        for css_name in self.compos_css:
            self.css_script += self.compos_css[css_name].css_script

    def add_compo_html(self, compo_html):
        '''
        :param compo_html: HTML obj in a compo
        '''
        self.compos_html += [compo_html]
        self.html_body += compo_html.html_script
        self.html_script = self.html_header + self.html_body + self.html_end

    def add_compo_css(self, compo_css):
        '''
        :param compo_css: directory of CSS objs, {'.class'/'#id' : CSS obj}
        '''
        self.compos_css.update(compo_css)
        self.init_page_css()

    def export(self, directory='page', html_file_name='xml.html', css_file_name='xml.css'):
        os.makedirs(directory, exist_ok=True)
        open(os.path.join(directory, html_file_name), 'w').write(self.html_script)
        open(os.path.join(directory, css_file_name), 'w').write(self.css_script)
        return self.html_script, self.css_script
