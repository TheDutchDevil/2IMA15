class VerticalDecomposition:

    edges = []

    def addEdge(self, edge):
        self.edges.append((edge, True))

    def addVertEdge(self, edge):
        self.edges.append((edge, False))
