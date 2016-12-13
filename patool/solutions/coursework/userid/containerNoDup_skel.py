#!/usr/bin/env python3
# This skeleton file is available at: http://www.macs.hw.ac.uk/~hwloidl/Courses/F21SC/Samples/containerNoDup_skel.py
# Implement a container class with methods for adding an element, extending with a list and a check for contains,
# and then implement a sub-class for a container that avoids adding duplicates (with the same methods).
# -------------------------------------------------------

class Container:
    """A very simple container class."""
    
    def __init__(self):
        """Initialise container to be an empty list."""
        self.container = []

    def __str__(self):
        """Show the contents of the container."""
        # use '{}' as brackets and ',' as separator
        value = "{"
        for item in self.container:
            value+= str(item) + ", "
        value.rstrip(", ")
        value += "}"
        return value
        
    def add(self, val):
        """Add an element @val@ to the container."""
        self.container.append(val)

    def extend(self, vals):
        """Add elements in @vals@ to the container.
         BUGGY: doesn't check for duplicates."""
        for val in vals:
            self.container.append(val)

    def contains(self, val):
        """Test whether a value @val@ is in a container."""
        return val in self.container

    def checkDups(self):
        """Check whether the container has duplicate elements."""
        found = []
        for val in self.container:
            if val in found:
                return True
            else:
                found.append(val)
        return False


   
class ContainerNoDup(Container):
    """A very simple container class."""

    def __init__(self):
        """Initialise container to be an empty list."""
        self.container = []

    def __str__(self):
        """Show the contents of the container."""
        # use '{}' as brackets and ',' as separator
        value = "{"
        for item in self.container:
            value += str(item) + ", "
        value = value.rstrip(", ")
        value += "}"
        return value

    def add(self, val):
        """Add an element @val@ to the container."""
        if not self.contains(val):
            self.container.append(val)

    def extend(self, vals):
        """Add elements in @vals@ to the container."""
        for val in vals:
            if not self.contains(val):
                self.container.append(val)


class Do:
    """A class for testing containers."""
    def Run(container_class):
        """Run a test script on an instance of @container_class@."""
        # Note: the argument container_class is the name of a class, not an instance
        print("-"*55)
        print("Testing: " + container_class.__doc__);
        c = container_class()
        c.add(9)
        print("After adding 9 ...")
        print(str(c))
        c.add(6)
        print("After adding 6 ...")
        print(str(c))
        l = [11, 3, 9, 17]
        c.extend(l)
        print("After adding " + str(l))
        print(str(c))
        print("Are there duplicate elements in the above list?")
        print(str(c.checkDups()))
        print("Testing whether 17 is in the container ...")
        print(str(c.contains(17)))
        print("Testing whether 13 is in the container ...")
        print(str(c.contains(13)))
        
# main program
if __name__ == '__main__':
    # with implementations of the classes Container, ContainerNoDup, and Tester above,
    # you can test the behaviour like this:
    Do.Run(Container)
    Do.Run(ContainerNoDup)
    
        
    
