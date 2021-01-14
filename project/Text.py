from Component import Component


# text component
class Text(Component):
    def __init__(self, word, location):
        Component.__init__(self, 'text', location)
        self.word = word

