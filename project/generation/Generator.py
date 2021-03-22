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
        self.page = None

    def reassign_compo_id(self):
        id = 0
        for c in self.compos:
            c.id = id
            id += 1

    def init_html_compos(self):
        for compo in self.compos:
            self.html_compos.append(HTMLCompo(compo))
        self.html_compos = sorted(self.html_compos, key=lambda x: x.location['top'])

    def init_page_html(self):
        if self.page is None:
            self.page = Page()
        for compo in self.html_compos:
            self.page.add_compo_html(compo.html)

    def init_page_css(self):
        if self.page is None:
            self.page = Page()
        for compo in self.html_compos:
            self.page.add_compo_css(compo.css)

    def export_page(self, export_dir='data/output/', html_file_name='xml.html', css_file_name='xml.css'):
        return self.page.export(directory=export_dir, html_file_name=html_file_name, css_file_name=css_file_name)
