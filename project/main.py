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
gen.slice_blocks()
# gen.visualize_blocks()
# gen.visualize_sections()
gen.init_page()
gen.export_page()


