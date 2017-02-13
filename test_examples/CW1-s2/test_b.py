
import unittest as ut
from tree import Tree

class TestTreeB(ut.TestCase):
    
    def test_find(self):
        my_tree = Tree(4)
        my_tree.insert(5)
        my_tree.insert(5)
        my_tree.insert(3)
        self.assertEqual(my_tree.find(4), 0)
        self.assertEqual(my_tree.find(3), 1)
        self.assertEqual(my_tree.find(2), -1)