class SortHelp:
    def splitLess(input, pivot):
        return [x for x in input if x < pivot]
    
    def splitEq(input, pivot):
        return [x for x in input if x == pivot]
    
    def splitGreat(input, pivot):
        return [x for x in input if x > pivot]
    