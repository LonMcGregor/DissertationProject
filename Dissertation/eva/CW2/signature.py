"""This test is designed to double check
that you meet the basic interface required
for taking part in the testing"""

import unittest as ut
from quicksort import quicksort

class TestQuickSort(ut.TestCase):
    
    def test_meets_interface(self):
        self.assertTrue(quicksort is not None)