"""cw1-s3 working solution file"""


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
        return self.find_internal(needle, 0)
    
    def find_internal(self, needle, depth):
        if self.value == needle:
            return depth
        if needle < self.value and self.left is not None:
            return self.left.find_internal(needle, depth+1)
        if needle > self.value and self.right is not None:
            return self.right.find_internal(needle, depth+1)
        return -1
        
