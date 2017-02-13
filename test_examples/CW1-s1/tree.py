"""CW1-s1 incorrect solution file"""


class Tree:
    def __init__(self, value):
        self.value = value

    def insert(self, value):
        return True

    def find(self, needle):
        return 0 if self.value == needle else -1

