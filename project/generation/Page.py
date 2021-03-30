import os
from generation.CSS import CSS


class Page:
    def __init__(self, title='Title', html_file_name='xml.html', css_file_name='xml.css'):
        self.html_file_name = html_file_name
        self.css_file_name = css_file_name

        self.compos_html = []   # list of HTML objs
        self.css = {}    # directory of CSS objs, {'.class'/'#id' : CSS obj}

        self.title = title
        self.html_header = None
        self.html_body = None
        self.html_end = "</body>\n</html>"

        self.html_script = ''
        self.css_script = ''
        self.js_script = ''

        self.set_global_page_style()
        self.init_page_css()
        self.init_page_js()
        self.init_page_html()

    def init_page_html(self):
        # header
        self.html_header = "<!DOCTYPE html>\n<html>\n<head>\n\t<title>" \
                           + self.title + "</title>\n" \
                           + "\t<link rel=\"stylesheet\" href=\"" + self.css_file_name + "\">\n" \
                           + "</head>\n"
        # body
        self.html_body = "<body>\n"
        for html in self.compos_html:
            self.html_body += html.html_script
        # assembly
        self.html_script = self.html_header + self.html_body + self.js_script + self.html_end

    def init_page_css(self):
        # self.css_script = 'ul{\n\tlist-style: None;\n\tpadding: 0;\n\tmargin:0;\n}\n'
        self.css_script = ''
        for css_name in self.css:
            self.css_script += self.css[css_name].css_script

    def set_global_page_style(self):
        '''
        Set styles of global tags/classes in one place
        '''
        self.css['p'] = CSS(name='p', margin='5px')
        self.css['table'] = CSS(name='table', width='100%', border='1px solid black')
        self.css['th'] = CSS(name='th', border='1px solid black')
        self.css['td'] = CSS(name='td', height='20px')
        self.css['input'] = CSS(name='input', margin='5px')
        self.css['label'] = CSS(name='label', margin='5px')
        self.css['table input'] = CSS(name='table input', width='97%', margin='0', border='1px solid black')

        # for compo
        self.css['.border-line'] = CSS(name='.border-line')  # for cutting line (ungrouped rectangle or line)
        # for normal div wrapper
        self.css['.content'] = CSS(name='.content', display='None')  # for content in a section that is not title
        self.css['.text-wrapper'] = CSS(name='.text-wrapper', justify_content='space-around')
        self.css['.input-wrapper'] = CSS(name='.input-wrapper')  # for wrapper that contains Input compound
        # for section
        self.css['.section-wrapper'] = CSS(name='.section-wrapper',
                                           background_color='#f1f1f1', margin='20px', padding='10px')  # for section-wrapper
        self.css['.section-title'] = CSS(name='.section-title',
                                         border='1px solid black', background_color='lightgrey', margin='5px',
                                         display='flex', justify_content='center', cursor='pointer')  # for section title
        self.css['.section-title:hover'] = CSS(name='.section-title:hover',
                                               background_color='darkgrey')

    def init_page_js(self):
        self.js_script = """
        <script>
        var sectionTitle = document.getElementsByClassName("section-title")
        for(let i = 0; i < sectionTitle.length; i++){
            sectionTitle[i].addEventListener("click", function () {
                this.classList.toggle("active")
                let sibling = this.nextElementSibling
                while(sibling){
                    if (sibling.style.display === "block" || sibling.style.display === "flex") {
                        sibling.style.display = "none";
                    } else {
                        if (sibling.classList.contains('input-wrapper')) {
                            sibling.style.display = "block";
                        }
                        else if (sibling.classList.contains('text-wrapper')){
                            sibling.style.display = "flex";
                        }
                    }
                    sibling = sibling.nextElementSibling
                }
            })
        }
        function addRow(ele) {
            let table = document.getElementById(ele.dataset.target)
            let rowNum = table.rows.length
            let row = table.insertRow(rowNum)
            for (let i=0; i < table.rows[rowNum - 1].cells.length; i++){
                let cell = row.insertCell(i)
                let cell_id = ele.dataset.target + '-col-' + i.toString() + '-row-' + rowNum.toString()
                cell.innerHTML = '<input id="' + cell_id + '">'
            }
        }
        </script>
    """

    def add_compo_html(self, compo_html):
        '''
        :param compo_html: HTML obj in a compo
        '''
        self.compos_html += [compo_html]
        self.html_body += compo_html.html_script
        self.html_script = self.html_header + self.html_body + self.js_script + self.html_end

    def add_compo_css(self, compo_css):
        '''
        :param compo_css: directory of CSS objs, {'.class'/'#id' : CSS obj}
        '''
        self.css.update(compo_css)
        self.init_page_css()

    def export(self, directory='page', html_file_name='xml.html', css_file_name='xml.css'):
        os.makedirs(directory, exist_ok=True)
        open(os.path.join(directory, html_file_name), 'w').write(self.html_script)
        open(os.path.join(directory, css_file_name), 'w').write(self.css_script)
        return self.html_script, self.css_script
