from obj.Element import Element

import string


# text component
class Text(Element):
    def __init__(self, content, location):
        super().__init__(type='text', location=location)
        self.type = 'text'
        self.content = content
        self.in_box = False         # whether be contained in a textbox
        self.is_guide_text = False     # whether the text guides an input unit

    def merge_text(self, text_b):
        text_a = self
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

        top = int((left_element.location['top'] + right_element.location['top']) / 2)
        left = left_element.location['left']
        right = right_element.location['right']
        bottom = int((left_element.location['bottom'] + right_element.location['bottom']) / 2)
        self.location = {'left': left, 'top': top, 'right': right, 'bottom': bottom}
        self.width = self.location['right'] - self.location['left']
        self.height = self.location['bottom'] - self.location['top']
        self.area = self.width * self.height
