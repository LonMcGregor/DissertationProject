"""CW1-s1 incorrect test case"""


import unittest as ut
from tree import Tree

class TestTree(ut.TestCase):
    
    def test_one(self):
        my_tree = Tree(4)
        self.assertTrue(False)