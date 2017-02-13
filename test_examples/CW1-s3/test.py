"""cw1-s3 working test case"""

import unittest as ut
from tree import Tree

class TestTree(ut.TestCase):
    
    def test_one(self):
        my_tree = Tree(4)
        self.assertTrue(my_tree.insert(5))
        self.assertFalse(my_tree.insert(5))
        self.assertTrue(my_tree.insert(3))
    
    def test_find(self):
        my_tree = Tree(4)
        my_tree.insert(5)
        my_tree.insert(5)
        my_tree.insert(3)
        self.assertEqual(my_tree.find(4), 0)
        self.assertEqual(my_tree.find(3), 1)
        self.assertEqual(my_tree.find(2), -1)