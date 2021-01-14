

# The parent class of all components including text and non-text
class Component:
    def __init__(self, type, location):
        self.type = type
        self.location = location
