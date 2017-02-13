"""CW2-s2 correct Solution file, multiple files"""

from sorthelp import SortHelp

def quicksort(input):
    if len(input) < 2:
        return input
    pivot = input[0]
    l = quicksort(SortHelp.splitLess(input, pivot))
    e = SortHelp.splitEq(input, pivot)
    g = quicksort(SortHelp.splitGreat(input, pivot))
    l.extend(e)
    l.extend(g)
    return l