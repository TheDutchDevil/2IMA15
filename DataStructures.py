from enum import Enum
import math as math

class Vector:
    """Represents a 2D vector."""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def cross(self, vec):
        """Returns the cross product of this vector with the provided vector."""
        return (self.x * vec.y) - (self.y * vec.x)

    def dot(self, vec):
        """Returns the dot product of this vector with the provided vector."""
        return (self.x * vec.x) + (self.y * vec.y)

    def squared_length(self):
        """Returns the squared length of the vector."""
        return self.x**2 + self.y**2

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

    def __hash__(self):
        return 17 * (hash(self.p1) + hash(self.p2))

    def __eq__(self, other):
        return self.p1 == other.p1 and self.p2 == other.p2

    def __ne__(self, other):
        return not self == other

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
    
    def asVector(self):
        """Returns a vector representation of this edge."""
        return Vector(self.getEndVertex().x - self.getStartVertex().x, self.getEndVertex().y - self.getStartVertex().y)
    
    def intersects(self, edge):
        """Returns true of this edge intersects with the provided edge."""
        p = self.getStartVertex()
        r = self.asVector()
        
        q = edge.getStartVertex()
        s = edge.asVector()
        
        if r.cross(s) == 0:
            return False
        else:
            # Define the vector between the start point p and q.
            pq = Vector(q.x - p.x, q.y - p.y)
        
            # This edge has line segment p + tr
            t = pq.cross(s) / r.cross(s)
            
            # The provided edge has line segment q + us
            u = pq.cross(r) / r.cross(s)
            
            return 0 <= t <= 1 and 0 <= u <= 1

    def slope(self):
        """Returns the slope of this edge or None if the edge is vertical (the slope is undefined in this case)."""
        if self.getStartVertex().x - self.getEndVertex().x == 0:
            return None
        else:
            return (self.getStartVertex().y - self.getEndVertex().y) / (self.getStartVertex().x - self.getEndVertex().x)

    def is_vertical(self):
        """Returns true if this edge is vertical. Otherwise false is returned."""
        return self.slope() == 0

    def getCorrespondingYValue(self, x):
        """
        Returns the y-value of the corresponding x-value on this edge.
        None is returned if this edge has no slope or the corresponding x-value is not part of this edge.
        """
        epsilon = 0.0001

        if self.getStartVertex().x <= x and x <= self.getEndVertex().x and self.slope() is not None:
            y_value = self.slope() * (x - self.getStartVertex().x) + self.getStartVertex().y

            # If the y-value is almost an integer, then round it.
            if abs(y_value % 1) < epsilon:
                y_value = math.floor(y_value)
            elif abs((y_value + epsilon) % 1) < epsilon:
                y_value = math.ceil(y_value + 1)

            return y_value
        else: return None

    def lies_above(self, edge):
        """Returns true if this edge lies above the provided edge."""
        return min(self.p1.y, self.p2.y) > min(edge.p1.y, edge.p2.y)

    def has_common_vertex(self, edge):
        """Returns true if this edge has a common vertex with the provided edge."""
        return self.p1 == edge.p1 or self.p1 == edge.p2 or \
               self.p2 == edge.p1 or self.p2 == edge.p2

class Vertex:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "({}, {})".format(self.x, self.y)

    def __hash__(self):
        return 19 * (hash(self.x) + hash(self.y))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self == other

    def liesAbove(self, edge):
        """Returns true if this vertex lies above the provided edge."""
        v_e = edge.asVector()
        v_v = Vector(self.x - edge.getEndVertex().x, self.y - edge.getEndVertex().y)

        return v_e.cross(v_v) > 0

    def lies_below(self, edge):
        """Returns true if this vertex lies below the provided edge."""
        v_e = edge.asVector()
        v_v = Vector(self.x - edge.getEndVertex().x, self.y - edge.getEndVertex().y)

        return v_e.cross(v_v) < 0

    def lies_on(self, edge):
        """Returns true if this vertex lies on the provided edge."""
        if self.isVertexOf(edge):
            return True

        # First, check for collinearity between the vertices.
        v_e = edge.asVector()
        v_vi = Vector(self.x - edge.getStartVertex().x, self.y - edge.getStartVertex().y)

        if v_e.cross(v_vi) == 0:
            # The points are collinear.
            # It remains to check that the vertex lies between the endpoints of the edge.
            v_v = Vector(self.x - edge.getStartVertex().x, self.y - edge.getStartVertex().y)
            dot_product = v_v.dot(v_e)

            return dot_product >= 0 and dot_product < v_e.squared_length()
        else: return False

    def isVertexOf(self, edge):
        """Returns true if this vertex is one of the edge its endpoints."""
        return edge.p1 == self or edge.p2 == self

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

    """The direction of the edge is undefined. The direction is not known."""
    Undefined = 9
