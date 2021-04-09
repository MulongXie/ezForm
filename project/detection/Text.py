from detection.Element import Element

import string
import cv2
import numpy as np


# text component
class Text(Element):
    def __init__(self, content, location):
        super().__init__(type='text', location=location)
        self.type = 'text'
        self.content = content
        self.in_box = False         # whether be contained in a textbox
        self.is_guide_text = False     # whether the text guides an input unit

    def merge_text(self, text_b, direction='h'):
        text_a = self
        text_b.is_abandoned = True

        top = min(text_a.location['top'], text_b.location['top'])
        left = min(text_a.location['left'], text_b.location['left'])
        right = max(text_a.location['right'], text_b.location['right'])
        bottom = max(text_a.location['bottom'], text_b.location['bottom'])
        self.location = {'left': left, 'top': top, 'right': right, 'bottom': bottom}
        self.width = self.location['right'] - self.location['left']
        self.height = self.location['bottom'] - self.location['top']
        self.area = self.width * self.height

        if direction == 'h':
            if text_a.location['left'] < text_b.location['left']:
                left_element = text_a
                right_element = text_b
            else:
                left_element = text_b
                right_element = text_a

            if right_element.content[0] in string.punctuation:
                self.content = left_element.content + right_element.content
            else:
                self.content = left_element.content + ' ' + right_element.content
        elif direction == 'v':
            if text_a.location['top'] < text_b.location['top']:
                top_element = text_a
                bottom_element = text_b
            else:
                top_element = text_b
                bottom_element = text_a

            self.content = top_element.content + '\n' + bottom_element.content

    def shrink_bound(self, binary_map):
        bin_clip = binary_map[self.location['top']:self.location['bottom'], self.location['left']:self.location['right']]
        height, width = np.shape(bin_clip)
        # print(self.location)
        # cv2.imshow('bin-clip', bin_clip)
        # cv2.waitKey()

        shrink_top = 0
        shrink_bottom = 0
        for i in range(height):
            # top
            if shrink_top == 0:
                if sum(bin_clip[i]) == 0:
                    shrink_top = 1
                else:
                    shrink_top = -1
            elif shrink_top == 1:
                if sum(bin_clip[i]) != 0:
                    self.location['top'] += i
                    shrink_top = -1
            # bottom
            if shrink_bottom == 0:
                if sum(bin_clip[height-i-1]) == 0:
                    shrink_bottom = 1
                else:
                    shrink_bottom = -1
            elif shrink_bottom == 1:
                if sum(bin_clip[height-i-1]) != 0:
                    self.location['bottom'] -= i
                    shrink_bottom = -1

            if shrink_top == -1 and shrink_bottom == -1:
                break

        shrink_left = 0
        shrink_right = 0
        for j in range(width):
            # left
            if shrink_left == 0:
                if sum(bin_clip[:, j]) == 0:
                    shrink_left = 1
                else:
                    shrink_left = -1
            elif shrink_left == 1:
                if sum(bin_clip[:, j]) != 0:
                    self.location['left'] += j
                    shrink_left = -1
            # right
            if shrink_right == 0:
                if sum(bin_clip[:, width-j-1]) == 0:
                    shrink_right = 1
                else:
                    shrink_right = -1
            elif shrink_right == 1:
                if sum(bin_clip[:, width-j-1]) != 0:
                    self.location['right'] -= j
                    shrink_right = -1

            if shrink_left == -1 and shrink_right == -1:
                break

        self.init_bound()

        # print(self.location)
        # bin_clip = binary_map[self.location['top']:self.location['bottom'], self.location['left']:self.location['right']]
        # cv2.imshow('bin-clip', bin_clip)
        # cv2.waitKey()
        # cv2.destroyWindow('bin-clip')
