from obj.Form import Form
from obj.Image import Image
import cv2

# *** 1. Elements detection ***
form = Form('data/3.jpg')
form.text_detection()
form.element_detection()
form.assign_element_ids()
form.visualize_all_elements()

# *** 2. Special element recognition ***
form.textbox_recognition()
form.visualize_all_elements()

# *** 3. Units grouping ***
form.group_elements_to_units()
form.sort_units()
form.visualize_units()

# *** 4. Table detection ***
form.table_detection()
form.table_refine()
form.visualize_all_elements()

# *** 5. Input compound recognition ***
form.input_compound_recognition()
form.visualize_inputs()


# board = form.img.img.copy()
# ******* show sorted elements ********
# elements = form.sort_elements(direction='v')
# for ele in elements:
#     print(ele.location)
#     ele.visualize_element(board)
#     cv2.imshow('b', board)
#     cv2.waitKey()

# ******* show elements relationship ********
# for text in form.texts:
#     board = form.img.img.copy()
#     for rec in form.rectangles:
#         if text.element_relation(rec) != 0:
#             text.visualize_element(board, (0,255,0), 2)
#             rec.visualize_element(board, (0,0,255),2, show=True)

# ******* show elements connection ********
# for i, u1 in enumerate(form.all_units):
#     board = form.img.img.copy()
#     u1.visualize_element(board, color=(0,0,255))
#     for j, u2 in enumerate(form.all_units):
#         if i == j:
#             continue
#         if u1.is_connected(u2, direction='h'):
#             u2.visualize_element(board, color=(0,255,0))
#             cv2.imshow('connected', board)
#             cv2.waitKey()
