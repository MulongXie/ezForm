from Form import Form
from Image import Image
import cv2

form = Form('data/3.jpg')
form.text_detection()
form.element_detection()
form.visualize_all_elements()
board = form.img.img.copy()

# ******* show sorted elements ********
# elements = form.sort_elements()
# for ele in elements:
#     print(ele.location)
#     color = None
#     if ele.type == 'text':
#         color = (0,255,0)
#     elif ele.type == 'rectangle':
#         color = (0,0,255)
#     elif ele.type == 'line':
#         color = (255,0,0)
#     ele.visualize_element(board, color=color, line=2)
# cv2.imshow('b', board)
# cv2.waitKey()


# ******* show elements relationship ********
# for text in form.texts:
#     board = form.img.img.copy()
#     for rec in form.rectangles:
#         if text.element_relation(rec) != 0:
#             text.visualize_element(board, (0,255,0), 2)
#             rec.visualize_element(board, (0,0,255),2, show=True)

form.textbox_detection()
form.visualize_all_elements()