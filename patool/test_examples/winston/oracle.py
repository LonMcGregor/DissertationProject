class Tree:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

    def add_child(self, value):
        if value == self.value:
            return
        if value < self.value:
            if self.left is None:
                self.left = Tree(value)
            else:
                self.left.add_child(value)
        if value > self.value:
            if self.right is None:
                self.right = Tree(value)
            else:
                self.right.add_child(value)

    def search(self, needle):
        if self.value == needle:
            return True
        if needle < self.value and self.left is not None:
            return self.left.search(needle)
        if needle > self.value and self.right is not None:
            return self.right.search(needle)
        return False
