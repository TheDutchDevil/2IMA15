"""
A module containing functions and classes related to the randomized incremental algorithm
that creates a trapezoidal deconstruction of a simple polygon.
"""
from random import shuffle
from DataStructures import Direction, Vertex, Edge

def randomize(collection):
    """
    Returns a new collection containing the same data as the provided collection,
    but in a random order.
    """
    # Copy the collection first to keep the old order intact.
    c_collection = list(collection)
    shuffle(c_collection)

    return c_collection

class Node:
    """A generic node."""
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return "_[{}]".format(self.data)

class XNode(Node):
    """A x-node that contains a vertex."""
    def __init__(self, vertex):
        super().__init__(vertex)

    def __repr__(self):
        return "X[{}]".format(self.data)

    def vertex(self):
        """Returns the vertex that is the data of this node."""
        return self.data

class YNode(Node):
    """A y-node that contains an edge."""
    def __init__(self, edge):
        super().__init__(edge)

    def __repr__(self):
        return "Y[{}]".format(self.data)

    def edge(self):
        """Returns the edge that is the data of this node."""
        return self.data


class TrapezoidLeaf(Node):
    """A trapezoid leaf that contains a trapezoid."""
    def __init__(self, trapezoid):
        super().__init__(trapezoid)

    def __repr__(self):
        return "T[{}]".format(self.data)

    def trapezoid(self):
        """Returns the trapezoid that is the data of this node."""
        return self.data

class TrapezoidSearchStructure:
    """A DAG for which the leaves are nodes of the type TrapezoidLeaf."""
    def __init__(self, root, left=None, right=None):
        self.root = root
        self.left = left
        self.right = right

    @staticmethod
    def from_bounding_box(bounding_box):
        """Initializes the trapezoid search structure from the given bounding box."""
        return TrapezoidSearchStructure(TrapezoidLeaf(bounding_box.as_trapezoid()))

    def point_location_query(self, vertex):
        """
        Runs a point location query on the tree with the specified vertex.
        Returns the TrapezoidLeaf in which it ends.
        """
        node = self.root

        if type(node) is XNode:
            if vertex.x < node.vertex().x:
                return self.get_left().pointLocationQuery(vertex)
            else: return self.get_right().pointLocationQuery(vertex)
        elif type(node) is YNode:
            if vertex.liesAbove(node.edge()):
                return self.get_right().pointLocationQuery(vertex)
            else: return self.get_left().pointLocationQuery(vertex)
        elif type(node) is TrapezoidLeaf:
            return node
        else:
            raise ValueError("The unkown node {} was encountered.".format(node))

    def get_left(self):
        """
        Returns the left child of the current node.
        Tthrows an LookupError if there is no left child.
        """
        if self.left is None:
            raise LookupError("No left child exists for {}.".format(self.root))
        return self.left

    def get_right(self):
        """
        Returns the right child of the current node.
        Throws an LookupError if there is no right child.
        """
        if self.right is None:
            raise LookupError("No right child exists for {}.".format(self.root))
        return self.right

class BoundingBox:
    """Represents a bounding box around a set of vertices."""
    def __init__(self, top_left, bottom_right):
        self.top_left = top_left
        self.bottom_right = bottom_right

    def __repr__(self):
        return "{}|\u203E _|{}".format(self.top_left, self.bottom_right)

    @staticmethod
    def around_vertices(vertices, padding=10):
        """Constructs a bounding box around the provided list of vertices.

        Arguments:
        vertices -- the list of vertices around which a bounding box is to be constructed.
        padding -- the padding between the bounding box and outer vertices (default 10).
        """
        if vertices == []:
            x_left = 0
            x_right = 0
            y_top = 0
            y_bottom = 0
        else:
            x_left = vertices[0].x
            x_right = vertices[0].x
            y_top = vertices[0].y
            y_bottom = vertices[0].y

            del vertices[0]

            for vertex in vertices:
                if vertex.x < x_left:
                    x_left = vertex.x
                if vertex.x > x_right:
                    x_right = vertex.x

                if vertex.y > y_top:
                    y_top = vertex.y
                if vertex.y < y_bottom:
                    y_bottom = vertex.y

        top_left = Vertex(x_left - padding, y_top + padding)
        bottom_right = Vertex(x_right + padding, y_bottom - padding)

        return BoundingBox(top_left, bottom_right)

    @staticmethod
    def around_edges(edges, padding=10):
        """Constructs a bounding box around the provided list of edges.

        Arguments:
        edges -- the list of edges around which a bounding box is to be constructed.
        padding -- the least between the bounding box and edges (default 10).
        """
        vertices = []

        for edge in edges:
            vertices.append(edge.getStartVertex())
            vertices.append(edge.getEndVertex())

        return BoundingBox.around_vertices(vertices, padding)

    def top_right(self):
        """Returns the top right vertex of the bounding box."""
        return Vertex(self.bottom_right.x, self.top_left.y)

    def bottom_left(self):
        """Returns the bottom left vertex of the bounding box."""
        return Vertex(self.top_left.x, self.bottom_right.y)

    def top(self):
        """Returns the top edge of the bounding box."""
        return Edge(self.top_left, self.top_right(), Direction.Right)

    def right(self):
        """Returns the right edge of the bounding box."""
        return Edge(self.top_right(), self.bottom_right, Direction.Right)

    def bottom(self):
        """Returns the bottom edge of the bounding box."""
        return Edge(self.bottom_right, self.bottom_left(), Direction.Right)

    def left(self):
        """Returns the left edge of the bounding box."""
        return Edge(self.bottom_left(), self.top_left, Direction.Right)

    def as_trapezoid(self):
        """Returns the trapezoid that represents the bounding box."""
        return Trapezoid(self.top_left, self.bottom_right, self.top(), self.bottom())

class Trapezoid:
    """A trapezoid defined by two vertices and two edges."""
    def __init__(self, leftp, rightp, top, bottom, neighbors_left=[], neighbors_right=[]):
        self.leftp = leftp
        self.rightp = rightp
        self.top = top
        self.bottom = bottom
        self.neighbors_left = neighbors_left
        self.neighbors_right = neighbors_right

    def __repr__(self):
        return "\u0394[lp {}, rp {}, top {}, btm {}]" \
            .format(self.leftp, self.rightp, self.top, self.bottom)

    def __eq__(self, other):
        return self.leftp == other.leftp and self.rightp == other.rightp and \
            self.top == other.top and self.bottom == other.bottom

    def __neq__(self, other):
        return not self == other

    def top_left(self):
        """Returns the left top vertex of the trapezoid."""
        # Find the y-value on the top edge.
        x_left = self.leftp.x
        y_top = self.top.getCorrespondingYValue(x_left)

        if y_top is None:
            raise ValueError('The top edge is vertical.')

        return Vertex(x_left, y_top)

    def top_right(self):
        """Returns the right top vertex of the trapezoid."""
        # Find the y-value on the top edge.
        x_right = self.rightp.x
        y_top = self.top.getCorrespondingYValue(x_right)

        if y_top is None:
            raise ValueError('The top edge is vertical.')

        return Vertex(x_right, y_top)

    def bottom_left(self):
        """Returns the bottom left vertex of the trapezoid."""
        # Find the y-value on the bototm edge.
        x_left = self.leftp.x
        y_bottom = self.bottom.getCorrespondingYValue(x_left)

        if y_bottom is None:
            raise ValueError('The bottom edge is vertical.')

        return Vertex(x_left, y_bottom)

    def bottom_right(self):
        """Returns the bottom right vertex of the trapezoid."""
        # Find the y-value on the bottom edge.
        x_right = self.rightp.x
        y_bottom = self.bottom.getCorrespondingYValue(x_right)

        if y_bottom is None:
            raise ValueError('The bottom edge is vertical.')

        return Vertex(x_right, y_bottom)

    def left(self):
        """Returns the left edge of the trapezoid."""
        top_l = self.top_left()
        bottom_l = self.bottom_left()

        if top_l == bottom_l:
            # The trapezoid does not have a left edge if the vertices are equal.
            return None
        else:
            return Edge(bottom_l, top_l, Direction.Undefined)

    def right(self):
        """Returns the left edge of the trapezoid."""
        top_r = self.top_right()
        bottom_r = self.bottom_right()

        if top_r == bottom_r:
            # The trapezoid does not have a right edge if the vertices are equal.
            return None
        else:
            return Edge(top_r, bottom_r, Direction.Undefined)

    def top_segment(self):
        """Returns the (paritial) top edge of the trapezoid."""
        top_l = self.top_left()
        top_r = self.top_right()

        return Edge(top_l, top_r, self.top.insideOn)

    def bottom_segment(self):
        """Returns the (paritial) bottom edge of the trapezoid."""
        bottom_l = self.bottom_left()
        bottom_r = self.bottom_right()

        return Edge(bottom_r, bottom_l, self.bottom.insideOn)
    
    def get_number_of_intersections(self, edge):
        """Returns the number of intersections that the provided edge has with this trapezoid."""
        top = self.top_segment()
        right = self.right()
        bottom = self.bottom_segment()
        left = self.left()

        return (1 if edge.intersects(top) else 0) + \
            (1 if edge.intersects(bottom) else 0) + \
            (1 if right is None and self.rightp.lies_on(edge) else 0) + \
            (1 if right is not None and edge.intersects(right) else 0) + \
            (1 if left is None and self.leftp.lies_on(edge) else 0) + \
            (1 if left is not None and edge.intersects(left) else 0)

    def is_intersected_by(self, edge):
        """Returns true if the provided edge intersects this trapezoid."""
        return self.get_number_of_intersections(edge) > 0

    def contains_vertex(self, vertex):
        """Returns tue if this trapezoids contains the provided vertex."""
        return self.leftp.x <= vertex.x and vertex.x <= self.rightp.x and \
            vertex.lies_below(self.top) and vertex.liesAbove(self.bottom)

    def split(self, edge):
        """Splits this trapezoid over the specified edge."""
        nr_of_intersections = self.get_number_of_intersections(edge)

        if nr_of_intersections == 0:
            if self.contains_vertex(edge.getStartVertex()) and self.contains_vertex(edge.getEndVertex()):
                # The trapezoid contains the whole edge.
                # First, define the most left and most right trapezoid.
                t_l = Trapezoid(self.leftp, edge.getStartVertex(), self.top, self.bottom)
                t_r = Trapezoid(edge.getEndVertex(), self.rightp, self.top, self.bottom)

                # Next, define the trapezoids split by the edge.
                t_t = Trapezoid(edge.getStartVertex(), edge.getEndVertex(), self.top, edge, [t_l], [t_r])
                t_b = Trapezoid(edge.getStartVertex(), edge.getEndVertex(), edge, self.bottom, [t_l], [t_r])

                # Define the neighbors of the most left and right trapezoid.
                t_l.neighbors_right = [t_t, t_b]
                t_r.neighbors_left = [t_t, t_b]

                return [t_l, t_t, t_b, t_r]
            else:
                # This trapezoid has nothing to do with this edge.
                return [self]
        elif nr_of_intersections == 1:
            # One of the edge its vertices lies in this trapezoid. Split this trapezoid vertically.
            if self.contains_vertex(edge.getStartVertex()):
                # Vertically split this trapezoid such that there is an empty trapezoid.
                # e.g. does not contain a vertex of the edge.
                empty_trapezoid = Trapezoid(self.leftp, edge.getStartVertex(), self.top, self.bottom, self.neighbors_left, [])

                # Replace the split trapezoid in its neighbors.
                for neighbor in empty_trapezoid.neighbors_left:
                    neighbor.neighbors_right.remove(self)
                    neighbor.neighbors_right.append(empty_trapezoid)

                # Construct the other trapezoid resulting from the vertical split.
                # This trapezoid is to be split horizontally. (Note the recursive call.)
                horizontal_split = Trapezoid(edge.getStartVertex(), self.rightp, self.top, self.bottom, [empty_trapezoid], self.neighbors_right).split(edge)

                # Define the neighbors after the split.
                empty_trapezoid.neighbors_right = [horizontal_split]

                return [empty_trapezoid].extend(horizontal_split)
            else:
                # Vertically split this trapezoid such that there is an empty trapezoid.
                # e.g. does not contain a vertex of the edge.
                empty_trapezoid = Trapezoid(edge.getEndVertex(), self.rightp, self.top, self.bottom, [], self.neighbors_right)
                
                # Replace the split trapezoid in its neighbors.
                for neighbor in empty_trapezoid.neighbors_right:
                    neighbor.neighbors_left.remove(self)
                    neighbor.neighbors_left.append(empty_trapezoid)

                # Construct the other trapezoid resulting from the vertical split.
                # This trapezoid is to be split horizontally. (Note the recursive call.)
                horizontal_split = Trapezoid(self.leftp, edge.getEndVertex(), self.top, self.bottom, self.neighbors_left, [empty_trapezoid]).split(edge)

                # Define the neighbors after the split.
                empty_trapezoid.neighbors_left = [horizontal_split]

                return [empty_trapezoid].extend(horizontal_split)
        else:
            # The edge crosses this whole trapezoid. Split this trapezoid horizontally.
            # First determine the left- and right vertex of the top and bottom trapezoid.
            if self.leftp.liesAbove(edge):
                leftp_t = self.leftp
                leftp_b = Vertex(self.leftp.x, self.bottom.getCorrespondingYValue(self.leftp.x))
            else:
                leftp_t = Vertex(self.leftp.x, self.top.getCorrespondingYValue(self.leftp.x))
                leftp_b = self.leftp

            if self.rightp.liesAbove(edge):
                rightp_t = self.rightp
                rightp_b = Vertex(self.rightp.x, self.bottom.getCorrespondingYValue(self.rightp.x))
            else:
                rightp_t = Vertex(self.rightp.x, self.top.getCorrespondingYValue(self.rightp.x))
                rightp_b = self.rightp

            # Next, determine the left- and right vertex of the intersecting edge.
            leftp_edge = Vertex(self.leftp.x, edge.getCorrespondingYValue(self.leftp.x))
            rightp_edge = Vertex(self.rightp.x, edge.getCorrespondingYValue(self.rightp.x))

            # Give preference to an actually existing vertex.
            # If the vertex on the intersecting edge is one of its endpoints and the one determined above is not, override it.
            if leftp_edge.isVertexOf(edge):
                if not leftp_t.isVertexOf(self.top):
                    leftp_t = leftp_edge
                if not leftp_b.isVertexOf(self.bottom):
                    leftp_b = leftp_edge
            if rightp_edge.isVertexOf(edge):
                if not rightp_t.isVertexOf(self.top):
                    rightp_t = rightp_edge
                if not rightp_b.isVertexOf(self.bottom):
                    rightp_b = rightp_edge

            t_top = Trapezoid(leftp_t, rightp_t, self.top, edge, [], [])
            t_bottom = Trapezoid(leftp_b, rightp_b, edge, self.bottom, [], [])

            # Determine the neighbors of these new trapezoids.
            for neighbor in self.neighbors_left:
                # Remove this split trapezoid from its left neighbors.
                neighbor.neighbors_right.remove(self)

                # If true, the trapezoid lies above the new edge that splits this trapezoid.
                if neighbor.bottom.lies_above(edge) or neighbor.bottom == edge:
                    t_top.neighbors_left.append(neighbor)
                    neighbor.neighbors_right.append(t_top)

                # If true, the trapezoid lies below the new edge that splits this trapezoid.
                if edge.lies_above(neighbor.top) or neighbor.top == edge:
                    t_bottom.neighbors_left.append(neighbor)
                    neighbor.neighbors_right.append(t_bottom)

                # If the trapezoid lies both above and below the new edge.
                if edge.lies_above(neighbor.bottom) and neighbor.top.lies_above(edge):
                    t_top.neighbors_left.append(neighbor)
                    t_bottom.neighbors_left.append(neighbor)

                    neighbor.neighbors_right.append(t_top)
                    neighbor.neighbors_right.append(t_bottom)

            for neighbor in self.neighbors_right:
                # Remove this split trapezoid from its right neighbors.
                neighbor.neighbors_left.remove(self)

                # If true, the trapezoid lies above the new edge that splits this trapezoid.
                if neighbor.bottom.lies_above(edge) or neighbor.bottom == edge:
                    t_top.neighbors_right.append(neighbor)
                    neighbor.neighbors_left.append(t_top)

                # If true, the trapezoid lies below the new edge that splits this trapezoid.
                if edge.lies_above(neighbor.top) or neighbor.top == edge:
                    t_bottom.neighbors_right.append(neighbor)
                    neighbor.neighbors_left.append(t_bottom)

                # If the trapezoid lies both above and below the new edge.
                if edge.lies_above(neighbor.bottom) and neighbor.top.lies_above(edge):
                    t_top.neighbors_right.append(neighbor)
                    t_bottom.neighbors_right.append(neighbor)

                    neighbor.neighbors_left.append(t_top)
                    neighbor.neighbors_left.append(t_bottom)

            return [t_top, t_bottom]

class TrapezoidalDecomposition:
    """Contains the functions related to the trapezoidal decomposition of a simple polygon."""

    @staticmethod
    def _find_intersections(trapezoid, edge, intersections):
        """Recursively check the neighboring trapezoids to find all intersections."""
        intersections.append(trapezoid)

        for left_neighbor in trapezoid.neighbors_left:
            if not intersections.contains(left_neighbor) and left_neighbor.is_intersected_by(edge):
                intersections = TrapezoidalDecomposition._find_intersections( \
                    left_neighbor, edge, intersections)

        for right_neighbor in trapezoid.neighbors_right:
            if not intersections.contains(right_neighbor) and \
                    right_neighbor.is_intersected_by(edge):

                intersections = TrapezoidalDecomposition._find_intersections( \
                    right_neighbor, edge, intersections)

        return intersections

    @staticmethod
    def find_intersected_trapezoids(start, edge):
        """Returns the intersections of the specified edge with the trapezoids."""
        return TrapezoidalDecomposition._find_intersections(start, edge, [])

def decompose_basic(edges):
    """
    Runs the basic randomized incremental algorithm on the provided collection of edges.
    Returns the vertical decomposition.
    """
    r = BoundingBox.around_edges(edges)
    edges = randomize(edges)

    d = TrapezoidSearchStructure.from_bounding_box(r)

    for edge in edges:
        start = d.point_location_query(edge.getStartVertex())
        trapezoids = TrapezoidalDecomposition.find_intersected_trapezoids(start.trapezoid(), edge)

    # TODO: Implement further.
