"""This test is designed to double check
that you meet the basic interface required
for taking part in the testing"""

import unittest as ut
from tree import Tree

class TestTree(ut.TestCase):
    
    def test_meets_interface(self):
        t = Tree(0)
        methods = t.__dir__()
        self.assertIn("__init__", methods)
        self.assertIn("insert", methods)
        self.assertIn("find", methods)