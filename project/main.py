from detection.Form import *
from generation.Generator import Generator


form = form_compo_detection('data/input/3.jpg')
form.visualize_detection_result()

gen = Generator(form)
gen.init_html_compos()
gen.slice_blocks()
# gen.visualize_blocks()
# gen.visualize_sections()
gen.init_page(by='section')
html, css = gen.export_page()

