import os
import sys
import base64
import cv2

# *** set project root directory ***
root = '/'.join(__file__.split('/')[:-1])
sys.path.append(os.path.join(root, 'detection'))
sys.path.append(os.path.join(root, 'generation'))
# **********************************

from detection.Form import *
from generation.Generator import Generator


# form_img_file = 'data/input/2.jpg'
form_img_file = sys.argv[1]

form = form_compo_detection(form_img_file)
# form.visualize_detection_result()

gen = Generator(form)
gen.init_html_compos()
gen.group_html_compos_by_unit_group_id()
gen.slice_block_by_group()
# gen.visualize_blocks()
# gen.visualize_sections()
# gen.visualize_compos_groups()
# gen.init_page_html(by='block')
gen.init_page()
gen.export_page()


