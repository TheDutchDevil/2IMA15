from DataStructures import Direction, Vertex, Edge
from random import shuffle

def constructBoundingBox(vertices, padding = 10):
    """Constructs a bounding box around the provided list of vertices.
    
    Arguments:
    vertices -- the list of vertices around which a bounding box is to be constructed.
    padding -- the padding between the bounding box and outer vertices (default 10).
    """
    if vertices == []:
        xLeft = 0
        xRight = 0
        yTop = 0
        yBottom = 0
    else:
        xLeft = vertices[0].x
        xRight = vertices[0].x
        yTop = vertices[0].y
        yBottom = vertices[0].y
        
        del vertices[0]
        
        for vertex in vertices:
            if vertex.x < xLeft:
                xLeft = vertex.x
            if vertex.x > xRight:
                xRight = vertex.x
            
            if vertex.y > yTop:
                yTop = vertex.y
            if vertex.y < yBottom:
                yBottom = vertex.y
    
    topLeft = Vertex(xLeft - padding, yTop + padding)
    bottomRight = Vertex(xRight + padding, yBottom - padding)
    
    return BoundingBox(topLeft, bottomRight)
    
def randomize(collection):
    """Returns a new collection containing the same data as the provided collection, but in a random order."""
    # Copy the collection first to keep the old order intact.
    cCollection = list(collection)
    shuffle(cCollection)
    
    return cCollection

# A generic node.
class Node:
    def __init__(self, data):
        self.data = data
        
    def __repr__(self):
        return "_[{}]".format(self.data)

# A x-node that contains a vertex.
class XNode(Node):
    def __init__(self, vertex):
        super().__init__(vertex)
        
    def __repr__(self):
        return "X[{}]".format(self.data)
    
    def vertex(self): return self.data

# A y-node that contains an edge. 
class YNode(Node):
    def __init__(self, edge):
        super().__init__(edge)
        
    def __repr__(self):
        return "Y[{}]".format(self.data)
        
    def edge(self): return self.data

# A trapezoid leaf that contains a trapezoid.
class TrapezoidLeaf(Node):
    def __init__(self, trapezoid):
        super().__init__(trapezoid)
        
    def __repr__(self):
        return "T[{}]".format(self.data)
        
    def trapezoid(self): return self.data

# A DAG for which the leaves are nodes of the type TrapezoidLeaf.
class TrapezoidSearchStructure:
    def __init__(self, root, left = None, right = None):
        self.root = root
        self.left = left
        self.right = right        
    
    def fromBoundingBox(bb):
        """Initializes the trapezoid search structure from the given bounding box."""
        return TrapezoidSearchStructure(TrapezoidLeaf(bb.asTrapezoid()))
    
    def pointLocationQuery(self, vertex):
        """Runs a point location query on the tree with the specified vertex and returns the TrapezoidLeaf in which it ends."""
        node = self.root
        
        if type(node) is XNode:
            if vertex.x < node.vertex().x: return self.getLeft().pointLocationQuery(vertex)
            else: return self.getRight().pointLocationQuery(vertex)
        elif type(node) is YNode:
            if vertex.liesAbove(node.edge()): return self.getRight().pointLocationQuery(vertex)
            else: return self.getLeft().pointLocationQuery(vertex)
        elif type(node) is TrapezoidLeaf:
            return node
        else:
            raise ValueError("The unkown node {} was encountered.".format(node))
    
    def getLeft(self):
        """Returns the left child of the current node, or throws an LookupError if there is no left child."""
        if self.left is None:
            raise LookupError("No left child exists for {}.".format(self.root))
        return self.left
        
    def getRight(self):
        """Returns the right child of the current node, or throws an LookupError if there is no right child."""
        if self.right is None:
            raise LookupError("No right child exists for {}.".format(self.root))
        return self.right
        
class BoundingBox:
    def __init__(self, topLeft, bottomRight):
        self.topLeft = topLeft
        self.bottomRight = bottomRight
        
    def __repr__(self):
        return "{}|\u203E _|{}".format(self.topLeft, self.bottomRight)
    
    def topRight(self):
        """Returns the top right vertex of the bounding box."""
        return Vertex(self.bottomRight.x, self.topLeft.y)
    
    def bottomLeft(self):
        """Returns the bottom left vertex of the bounding box."""
        return Vertex(self.topLeft.x, self.bottomRight.y)
    
    def top(self):
        """Returns the top edge of the bounding box."""
        return Edge(self.topLeft, self.topRight(), Direction.Right)
        
    def right(self):
        """Returns the right edge of the bounding box."""
        return Edge(self.topRight(), self.bottomRight, Direction.Right) 
        
    def bottom(self):
        """Returns the bottom edge of the bounding box."""
        return Edge(self.bottomRight, self.bottomLeft(), Direction.Right)
    
    def left(self):
        """Returns the left edge of the bounding box."""
        return Edge(self.bottomLeft(), self.topLeft, Direction.Right)
    
    def asTrapezoid(self):
        """Returns the trapezoid that represents the bounding box."""
        return Trapezoid(self.topLeft, self.bottomRight, self.top(), self.bottom())

class Trapezoid:
    def __init__(self, leftp, rightp, top, bottom, leftNeighbors = [], rightNeighbors = []):
        self.leftp = leftp
        self.rightp = rightp
        self.top = top
        self.bottom = bottom
        self.leftNeighbors = leftNeighbors
        self.rightNeighbors = rightNeighbors
    
    def __repr__(self):
        return "\u0394[lp {}, rp {}, top {}, btm {}]".format(self.leftp, self.rightp, self.top, self.bottom)