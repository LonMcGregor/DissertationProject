"""CW2-s1 incorrect test case"""

import unittest as ut
from quicksort import quicksort

class TestQuickSort(ut.TestCase):
    
    def test_one(self):
        result = quicksort([0,2,3])
        self.assertEqual(result, [0,2,3])