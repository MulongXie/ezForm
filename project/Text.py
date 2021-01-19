# text component
class Text:
    def __init__(self, word, location):
        self.type = 'text'
        self.word = word
        self.location = location            # {left, top, width, height}
        self.width = location['width']
        self.height = location['height']
