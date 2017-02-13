"""CW1-s2 working solution in multiple files"""

from internals import find_internal

class Tree:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

    def insert(self, value):
        if value == self.value:
            return False
        if value < self.value:
            if self.left is None:
                self.left = Tree(value)
                return True
            else:
                return self.left.insert(value)
        if value > self.value:
            if self.right is None:
                self.right = Tree(value)
                return True
            else:
                return self.right.insert(value)

    def find(self, needle):
        return find_internal(self, needle, 0)
    