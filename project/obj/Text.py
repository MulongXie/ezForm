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

            if bottom_element.content[0] in string.punctuation:
                self.content = top_element.content + bottom_element.content
            else:
                self.content = top_element.content + ' ' + bottom_element.content


