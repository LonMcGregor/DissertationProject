# ANA
# TEST

import unittest as ut
from tree import Tree

class TestTree(ut.TestCase):
    
    def test_add(self):
        b = Tree(4)
        self.assertTrue(b.search(4))
