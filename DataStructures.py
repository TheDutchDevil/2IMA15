from enum import Enum

# Represents an edge from p1 to p2
class Edge:

    # insideOn captures on what side of the edge the inside of the polygon lies. Can be left, right or both (for edges
    # that are part of the decomposition)
    def __init__(self, p1, p2, insideOn):
        self.p1 = p1
        self.p2 = p2
        self.insideOn = insideOn

    def __repr__(self):
        return "({}, {})".format(self.p1, self.p2)

    def startYOfEdge(self):
        return self.p1.y if self.p1.x < self.p2.x else self.p2.y

    def statusKeyForEdge(self):
        dx = abs(self.p1.x - self.p2.x)
        dy = self.getEndVertex().y - self.getStartVertex().y

        return StatusKey(self.getStartVertex().y, dy / dx)

    def getStartVertex(self):
        return self.p1 if self.p1.x < self.p2.x else self.p2

    def getEndVertex(self):
        return self.p2 if self.p1.x < self.p2.x else self.p1

    def pointAtEdge(self, targetX):
        return Vertex(targetX, self.getStartVertex().y + (targetX - self.getStartVertex().x) * \
                      ((self.getEndVertex().y - self.getStartVertex().y) /
                       (self.getEndVertex().x - self.getStartVertex().x)))

    def isLeftToRight(self):
        return not self.isRightToLeft()

    def isRightToLeft(self):
        return self.p1.x > self.p2.x

class Vertex:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "({}, {})".format(self.x, self.y)
    
    def liesAbove(self, edge):
        if edge.isLeftToRight():
            leftV = edge.p1
            rightV = edge.p2
        else:
            leftV = edge.p2
            rightV = edge.p1
        
        # Define vectors representing the edge and provided vertex.
        ve = Vertex(rightV.x - leftV.x, rightV.y - leftV.y)
        vv = Vertex(rightV.x - self.x, rightV.y - self.y)
        crossProd = ve.x * vv.y - ve.y * vv.x
        
        return crossProd < 0


# Used for the sweep line
class StatusKey:
    def __init__(self, startAtY, dxdy):
        self.startAtY = startAtY
        self.dxdy = dxdy

    def __lt__(self, other):
        if self.startAtY == other.startAtY:
            return self.dxdy < other.dxdy
        else:
            return self.startAtY < other.startAtY

    def __eq__(self, other):
        return self.startAtY == other.startAtY and self.dxdy == other.dxdy

    def __ne__(self, other):
        return not self == other

    def __ge__(self, other):
        return not self < other

    def __le__(self, other):
        return (self < other) or (self == other)

    def __gt__(self, other):
        return not self <= other

    def __repr__(self):
        return "(start: {}, dxdy: {})".format(self.startAtY, self.dxdy)


class Direction(Enum):
    Left = 1
    Right = 2
    Both = 3
