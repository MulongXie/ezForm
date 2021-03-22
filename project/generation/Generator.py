from detection.Form import Form
from generation.Page import Page
from generation.HTML import HTML
from generation.HTMLCompo import HTMLCompo

import os


class Generator:
    def __init__(self, form):
        self.form = form
        self.compos = form.get_detection_result()
        self.reassign_compo_id()

        self.html_compos = []
        self.html_page = None

    def reassign_compo_id(self):
        id = 0
        for c in self.compos:
            c.id = id
            id += 1

    def init_HTML_compos(self):
        for compo in self.compos:
            self.html_compos.append(HTMLCompo(compo))

    def init_HTML_page(self):
        self.html_page = Page()
        for compo in self.html_compos:
            self.html_page.add_compo_html(compo.html_script)

    def export_page(self, export_dir='data/output/', html_file_name='xml.html', css_file_name='xml.css'):
        return self.html_page.export(directory=export_dir, html_file_name=html_file_name, css_file_name=css_file_name)
