"""CW2-s2 correct test case, multiple files"""

import unittest as ut
from testb import my_assert

class TestQuickSort(ut.TestCase):
    
    def test_one(self):
        self.assertTrue(my_assert([0,1,2,3], [0,1,2,3])
        self.assertTrue(my_assert([2,1,3,0], [0,1,2,3])
        self.assertTrue(my_assert([2,1,3,3], [1,2,3,3])