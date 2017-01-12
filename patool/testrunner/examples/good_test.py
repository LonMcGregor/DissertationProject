import unittest as ut
from broken_tree import BrokenTree

class TestBrokenTreee(ut.TestCase):
    
    def test_add(self):
        b = BrokenTree(4)
        self.assertTrue(b.search(4))
        self.assertFalse(b.search(5))
        b.add_child(5)
        self.assertTrue(b.search(5))

    def test_order(self):
        b = BrokenTree(4)
        b = BrokenTree(3)
        b = BrokenTree(5)
        self.assertTrue(b.value == 4)
        self.assertTrue(b.left.value == 3)
        self.assertTrue(b.right.value == 5)