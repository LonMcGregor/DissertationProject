import unittest as ut
from broken_tree import BrokenTree

class TestBrokenTreee(ut.TestCase):
    
    def test_add(self):
        b = BrokenTree(4)
        self.assertTrue(b.search(4))
