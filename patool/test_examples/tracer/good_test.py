# TRACER
# TEST

import unittest as ut
from tree import Treee

class TestBrokenTreee(ut.TestCase):
    
    def test_add(self):
        b = Treee(4)
        self.assertTrue(b.search(4))
        self.assertFalse(b.search(5))
        b.add_child(5)
        self.assertTrue(b.search(5))

    def test_order(self):
        b = Treee(4)
        b = Treee(3)
        b = Treee(5)
        self.assertTrue(b.value == 4)
        self.assertTrue(b.left.value == 3)
        self.assertTrue(b.right.value == 5)