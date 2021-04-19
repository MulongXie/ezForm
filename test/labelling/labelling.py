from glob import glob
from os.path import join as pjoin
import cv2
import json

gb_x, gb_y = -1, -1
gb_labels = []
gb_img = None
gb_flag_ctn = True


def mouse_actions(event, x, y, flags, params):
    global gb_x, gb_y, gb_img, gb_flag_ctn
    if event == cv2.EVENT_LBUTTONDOWN:
        if gb_flag_ctn:
            gb_x, gb_y = x, y
            gb_flag_ctn = False
            gb_img = cv2.circle(gb_img, (x, y), 5, (0,0,255), 2)
            cv2.imshow('img', gb_img)
        else:
            print("Enter type (1-5)")


def label_img(img_file, output_dir=''):
    img_name = img_file.split('\\')[-1][:-4]
    label_file = pjoin(output_dir, img_name + '.json')

    img = cv2.imread(img_file)
    global gb_img, gb_labels, gb_flag_ctn
    gb_img = img
    cv2.imshow('img', img)
    cv2.setMouseCallback('img', mouse_actions)
    while True:
        global gb_x, gb_y
        key = chr(cv2.waitKey(0))

        if key in ('1', '2', '3', '4', '5'):
            label = {'x': gb_x, 'y': gb_y, 'type':key}
            if not gb_flag_ctn:
                gb_flag_ctn = True
                gb_labels.append(label)
            else:
                gb_labels[-1] = label
            print(gb_labels)
        elif key == 'q':
            print("Number of labels:", len(gb_labels))
            cv2.destroyWindow('img')
            json.dump(gb_labels, open(label_file, 'w'), indent=4)
            break
        else:
            print("Enter options: '1-5' to label; 'q' to continue to the next img\n")


def label_img_batch(data_dir='E:\\Mulong\\Datasets\\form\\input'):
    img_files = glob(pjoin(data_dir, '*'))
    for img_file in img_files:
        print(img_file)
        label_img(img_file)


# label_img('1.jpg')
label_img_batch()

