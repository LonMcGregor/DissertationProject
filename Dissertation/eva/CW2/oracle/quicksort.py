"""This is a complete implementation"""

def quicksort(input):
    if len(input) < 2:
        return input
    pivot = input[0]
    l = quicksort([x for x in input if x < pivot])
    e = [x for x in input if x == pivot]
    g = quicksort([x for x in input if x > pivot])
    l.extend(e)
    l.extend(g)
    return l
