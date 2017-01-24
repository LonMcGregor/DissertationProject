# LUCIO
# TEST

import unittest as ut
from tree import Tree

class TestTree(ut.TestCase):
    
    def test_add(self):
        b = Tree(4)
        self.assertTrue(b.search(4))
        self.assertFalse(b.search(5))
        b.add_child(5)
        self.assertTrue(b.search(5))

    def test_order(self):
        b = Tree(4)
        b = Tree(3)
        b = Tree(5)
        self.assertTrue(b.value == 4)
        self.assertTrue(b.left.value == 3)
        self.assertTrue(b.right.value == 5)