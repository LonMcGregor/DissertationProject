"""CW2-s3 correct test case"""

import unittest as ut
from quicksort import quicksort

class TestQuickSort(ut.TestCase):
    
    def test_one(self):
        result = quicksort([0])
        self.assertEqual(result, [0])
        result = quicksort([0,1,2,3])
        self.assertEqual(result, [0,1,2,3])
        result = quicksort([3,2,1,0])
        self.assertEqual(result, [0,1,2,3])
        result = quicksort([2,0,0,3])
        self.assertEqual(result, [0,0,2,3])