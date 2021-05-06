import os
import sys
import fitz
# *** set project root directory ***
root = '/'.join(__file__.split('/')[:-1])
sys.path.append(os.path.join(root, 'detection'))
sys.path.append(os.path.join(root, 'generation'))
# **********************************

from detection.Form import *
from generation.Generator import *


def form_img_process(img_file, export_dir):
    form = form_compo_detection(form_img_file_name=img_file, export_dir=export_dir)
    form.visualize_detection_result()

    gen = Generator(form, export_dir=export_dir)
    gen.init_html_compos()
    gen.group_html_compos_by_unit_group_id()
    gen.slice_block_by_group()
    # gen.visualize_blocks()
    # gen.visualize_sections()
    # gen.visualize_compos_groups()
    # gen.init_page_html(by='block')
    gen.init_page()
    gen.export_page()


# form_img_file = 'data/input/2.jpg'
form_img_file = sys.argv[1]

# *** multi-page PDF ***
if form_img_file.split('.')[-1].lower() == 'pdf':
    pdf_name = (form_img_file.split('/')[-1]).split('.')[0]
    output_dir = 'data/output/pdf-' + pdf_name
    os.makedirs(output_dir, exist_ok=True)

    paths = []
    doc = fitz.open(form_img_file)
    for pg in range(doc.pageCount):
        page = doc[pg]
        rotate = int(0)
        zoom_x = 1.0
        zoom_y = 1.0
        trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
        pm = page.getPixmap(matrix=trans, alpha=False)

        page_dir = "%s/%s_%d" % (output_dir, pdf_name, pg + 1)
        os.makedirs(page_dir, exist_ok=True)
        page_img_file = page_dir + "/%s_%d.jpg" % (pdf_name, pg + 1)
        pm.writePNG(page_img_file)
        form_img_process(page_img_file, page_dir)

        result_dir = page_dir + "/%s_%d" % (pdf_name, pg + 1) + "/"
        paths.append({"inputImg": page_img_file, "resultImg": result_dir + "detection.jpg",
                      "resultPage": result_dir + 'xml.html', "compoLocFile": result_dir + "input_loc.json"})
    print(paths)
# *** single image ***
else:
    form_img_process(form_img_file, 'data/output/')
