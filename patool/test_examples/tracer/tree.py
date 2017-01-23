# CHEER UP LUV, THE CAVALRY'S HERE!

class Tree:
    
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
    
    def add_child(self, value):
        self.left = BrokenTree(value)
    
    def search(self, needle):
        if self.value == needle:
            return True
        if self.left:
            return self.left.search(needle)
        return False
