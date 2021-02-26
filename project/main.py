from Form import Form
from Image import Image
import cv2

form = Form('data/3.jpg')
form.text_detection()
form.element_detection()
# form.visualize_all_elements()

elements = form.sort_elements()
board = form.img.img
for ele in elements:
    print(ele.location)
    color = None
    if ele.type == 'text':
        color = (0,255,0)
    elif ele.type == 'rectangle':
        color = (0,0,255)
    elif ele.type == 'line':
        color = (255,0,0)
    ele.visualize_element(board, show=True, color=color, line=2)