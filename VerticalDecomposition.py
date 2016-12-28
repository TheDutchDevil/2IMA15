class VerticalDecomposition:

    # list of tuples (a, b) where a is an edge in the decomposition and b is true iff a is an edge of the original
    # polygon.
    edges = []

    def addEdge(self, edge):
        self.edges.append((edge, True))

    def addVertEdge(self, edge):
        self.edges.append((edge, False))
