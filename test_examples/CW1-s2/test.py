"""CW1-s2 working test case in multiple files"""

import unittest as ut
from tree import Tree

class TestTree(ut.TestCase):
    
    def test_one(self):
        my_tree = Tree(4)
        self.assertTrue(my_tree.insert(5))
        self.assertFalse(my_tree.insert(5))
        self.assertTrue(my_tree.insert(3))
    