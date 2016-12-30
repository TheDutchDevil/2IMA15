from DataStructures import Vertex, Edge
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
    topRight = Vertex(xRight + padding, yTop + padding)
    bottomLeft = Vertex(xLeft - padding, yBottom - padding)
    bottomRight = Vertex(xRight + padding, yBottom - padding)
    
    return BoundingBox(topLeft, topRight, bottomLeft, bottomRight)

def randomize(collection):
    """Returns a new collection containing the same data as the provided collection, but in a random order."""
    # Copy the collection first to keep the old order intact.
    cCollection = list(collection)
    shuffle(cCollection)
    
    return cCollection
    

class BoundingBox:
    def __init__(self, topLeft, topRight, bottomLeft, bottomRight):
        self.topLeft = topLeft
        self.topRight = topRight
        self.bottomLeft = bottomLeft
        self.bottomRight = bottomRight
        
    def __repr__(self):
        return "{}|\u203E \u203E|{} | {}|_ _|{}".format(self.topLeft, self.topRight, self.bottomLeft, self.bottomRight)