"""CW1-s2 working solution in multiple files"""


def find_internal(tree, needle, depth):
    if tree.value == needle:
        return depth
    if needle < tree.value and tree.left is not None:
        return find_internal(tree.left, needle, depth+1)
    if needle > tree.value and tree.right is not None:
        return find_internal(tree.right, needle, depth+1)
    return -1