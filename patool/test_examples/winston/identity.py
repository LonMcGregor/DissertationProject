
import unittest as ut
from tree import Tree

class TestTree(ut.TestCase):
    
    def test_meets_interface(self):
        methods = Tree.__dir__()
        self.assertIn("add_child", methods)
        self.assertIn("search", methods)
