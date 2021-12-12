class Character():
    def __init__(self, name, color=None, image=None):
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, Character):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.name == other.name
