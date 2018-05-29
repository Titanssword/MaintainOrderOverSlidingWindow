def merge(self, other):
    # Grow until self has at least as many compactors as other
    while self.H < other.H: self.grow()
    # Append the items in same height compa  kctors
    for h in range(other.H): self.compactors[h].extend(other.compactors[h])
    self.size = sum(len(c) for c in self.compactors)
    # Keep compressing until the size constraint is met
    while self.size >= self.maxSize:
        self.compress()
    assert(self.size < self.maxSize)
