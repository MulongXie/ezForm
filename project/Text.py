from Element import Element


# text component
class Text(Element):
    def __init__(self, word, location):
        super().__init__(type='text', location=location)
        self.type = 'text'
        self.word = word
        self.in_box = False     # whether be contained in a textbox
