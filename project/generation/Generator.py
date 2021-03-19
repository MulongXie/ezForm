from detection.Form import Form
from generation.Page import Page
from generation.HTML import HTML
from generation.HTMLCompo import HTMLCompo


class Generator:
    def __init__(self, form):
        self.form = form
        self.compos = form.get_detection_result()

        self.HTML_compos = []
        self.HTML_page = None

    def init_HTML_compos(self):
        for compo in self.compos:
            self.HTML_compos.append(HTMLCompo(compo))

    def init_HTML_page(self):
        self.HTML_page = Page()
        for compo in self.HTML_compos:
            self.HTML_page.add_compo(compo)

