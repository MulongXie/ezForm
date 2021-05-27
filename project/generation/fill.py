import fitz
import json
import base64
import sys
import cv2


def resize_img_by_height(org, resize_height):
    org_shape = org.shape
    resize_h = resize_height
    resize_w = int(org_shape[1] * (resize_h / org_shape[0]))
    org = cv2.resize(org, (resize_w, resize_h))
    return org


def get_rect_box(data):
    if data['type'] == 'text':
        print(data['fontSize'])
        width = fitz.getTextlength(text=data['text'], fontsize=int(data['fontSize'][:-2])) + 2
        height = int(data['fontSize'][:-2]) + 2
    elif data['type'] == 'img':
        width = float(data['width'][:-2])
        height = float(data['height'][:-2])

    rect_x1 = float(data['left'][:-2])
    rect_y1 = float(data['top'][:-2])
    rect_x2 = rect_x1 + width
    rect_y2 = rect_y1 + height

    return rect_x1, rect_y1, rect_x2, rect_y2


def fill_pdf(input_data_file, original_file, filled_result_dir):
    # read input data and original pdf
    input_data = json.load(open(input_data_file, 'r'))
    if original_file.split('.')[-1].lower() == 'pdf':
        # for pdf form, directly load it
        doc = fitz.open(original_file)
    else:
        # for image form, convert it to
        img = cv2.imread(original_file)
        if img.shape[0] > 1200:
            img = resize_img_by_height(img, 900)
            cv2.imwrite(filled_result_dir + 'resize.png', img)
            original_file = filled_result_dir + 'resize.png'
        src = fitz.open('pdf', fitz.open(original_file).convertToPDF())
        doc = fitz.open()
        page = doc.newPage(width=img.shape[1], height=img.shape[0])
        page.showPDFpage(page.rect, src)

    # fill data
    for data in input_data:
        page = doc[int(data['page']) - 1]
        if data['type'] == 'text':
            page.insertTextbox(get_rect_box(data), data['text'], fontsize=int(data['fontSize'][:-2]), color=(0, 0, 0))
        elif data['type'] == 'img':
            sig_img = filled_result_dir + data['page'] + '-' + data['id'] + '.png'
            open(sig_img, 'wb').write(base64.b64decode(data['img'].replace('data:image/png;base64,', '')))
            page.insertImage(get_rect_box(data), sig_img)
    doc.save(filled_result_dir + 'filled.pdf')


if __name__ == '__main__':

    # input_data_file='1-img/input.json', original_file='1-img/1.jpg', filled_result_dir='1-img/'
    # filled_data, input_form, result_dir = '../data/output/pdf-upload1/filled/input.json', '../data/upload/upload1.pdf', '../data/output/pdf-upload1/filled/'
    filled_data, input_form, result_dir = sys.argv[1:]

    fill_pdf(input_data_file=filled_data, original_file=input_form, filled_result_dir=result_dir)
